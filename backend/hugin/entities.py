"""FollowTheMoney 4.11 schema subset adapted to Pydantic and Mongo snapshots.

Upstream schema files and MIT license are retained in ftm_schema/. This adapter
does not claim to implement all FtM normalization or entity-resolution behavior.
"""
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from .models import fingerprint
from .sources import full_name


class Entity(BaseModel):
    id: str
    schema_name: Literal['Person', 'Company', 'Employment', 'Associate'] = Field(alias='schema')
    properties: dict[str, list[str]]

    @model_validator(mode='after')
    def required_properties(self):
        required = {'Person': ('name',), 'Company': ('name',), 'Employment': ('employee', 'employer'), 'Associate': ('person', 'associate')}
        if any(not self.properties.get(key) for key in required[self.schema_name]):
            raise ValueError('Entity is missing a required schema property')
        return self


def snapshot(job):
    contact = job['contact']
    person_id = 'dex-person-' + fingerprint(contact['id'])[:24]
    nodes, edges = [], []
    def add(schema, key, properties, status, evidence_ids=(), identity_confidence='unresolved', provenance='research'):
        entity = Entity(id=key, schema=schema, properties=properties).model_dump(by_alias=True)
        record = {'entity': entity, 'review_status': status, 'identity_confidence': identity_confidence, 'evidence_ids': list(evidence_ids), 'provenance': provenance}
        (edges if schema in ('Employment', 'Associate') else nodes).append(record)
        return key
    add('Person', person_id, {'name': [full_name(contact)]}, 'existing_contact_context', identity_confidence='known_dex_record', provenance='dex:' + contact['id'])
    # Company names alone are not enough to merge employers across contacts.
    if contact.get('company'):
        company_id = 'company-context-' + fingerprint({'contact': contact['id'], 'company': contact['company']})[:24]
        add('Company', company_id, {'name': [contact['company']]}, 'existing_contact_context', provenance='dex:' + contact['id'])
        props = {'employee': [person_id], 'employer': [company_id]}
        if contact.get('job_title'):
            props['role'] = [contact['job_title']]
        add('Employment', 'employment-context-' + fingerprint(props)[:24], props, 'existing_contact_context', provenance='dex:' + contact['id'])
    for finding in job['findings']:
        if finding['kind'] != 'company':
            continue
        company_id = 'company-claim-' + finding['id']
        add('Company', company_id, {'name': [finding['value']]}, finding['status'], finding['evidence_ids'], finding['identity_confidence'])
        add('Employment', 'employment-claim-' + finding['id'], {'employee': [person_id], 'employer': [company_id]}, finding['status'], finding['evidence_ids'], finding['identity_confidence'])
    for relation in job['relationships']:
        target = 'person-candidate-' + fingerprint({'job': job['id'], 'target': relation.get('target_url') or relation['target_name']})[:24]
        add('Person', target, {'name': [relation['target_name']]}, 'unresolved', relation['evidence_ids'])
        add('Associate', 'association-' + relation['id'], {'person': [person_id], 'associate': [target], 'relationship': [relation['relationship_type']]}, relation['status'], relation['evidence_ids'], relation['subject_identity_confidence'])
    return {'id': job['id'], 'job_id': job['id'], 'contact_id': contact['id'], 'created_at': job['created_at'], 'model': 'FollowTheMoney 4.11.0 schema subset', 'nodes': nodes, 'edges': edges, 'evidence_ids': [e['id'] for e in job['evidence']], 'notes': 'Existing Dex context is not new research. Name-only entities are not automatically merged. Relationship targets remain unresolved.'}
