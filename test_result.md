#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================
user_problem_statement: "Turn Hugin into a local, single-contact intelligence workspace with cited enrichment and verified Dex writeback."
backend:
  - task: "Durable contact enrichment, evidence, identity checks and sync-only recovery"
    implemented: true
    working: true
    file: "backend/hugin/engine.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "33 tests passed with HUGIN_TEST_MONGO_URL set. Actual MongoDB persistence/concurrency/recovery tested; research and Dex responses are fixtures. Live contact research/writeback remains unverified without a key and selected contact."
  - task: "Dex MCP adapter and live account readiness"
    implemented: true
    working: "NA"
    file: "backend/hugin/dex.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Fixture MCP/SSE/schema/error/retry tests pass. After restart, DEX_API_KEY is present but scoped to api.getdex.com. The owner chose a contact; MCP search failed authentication before contact retrieval. A read-only non-redirecting probe of api.getdex.com/v1 returned HTTP 502; documented REST uses api.prod.getdex.com. Edit the existing secure key binding to permit mcp.getdex.com. No live Dex mutation occurred."
frontend:
  - task: "Contacts, runs, evidence, connections and integration workspace"
    implemented: true
    working: true
    file: "frontend/src/workspace/Workspace.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Frozen dependency install, production build and Chromium fixture smoke pass. Ambiguous selector cannot start a run without a choice. No external requests on the private workspace. Archived components retained at /legacy."
metadata:
  created_by: "main"
  version: "2.0"
  test_sequence: 1
  run_ui: true
test_plan:
  current_focus:
    - "One owner-selected live Dex contact after secure key configuration"
  stuck_tasks:
    - "Live cited findings require a permitted professional source or usable cached research; authentication and empty-result note writeback are now verified"
  test_all: false
  test_priority: "high_first"
agent_communication:
  - agent: "main"
    message: "No testing sub-agent was invoked. Protected protocol block preserved. See docs/verification.md for exact commands, fixture/live distinctions, editorial limitations and remaining acceptance work."

# Subsequent owner-authorized live run, October 7, 2026
# Runtime revision 7 includes mcp.getdex.com; live Dex search found one the selected contact record.
# Job <PRIVATE_RUN_OR_NOTE_ID> saved and verified one additive note.
# No supported new findings: cached research absent; LinkedIn robots disallows extraction.
# Zero paid attempts. Existing contact fields and relationships preserved.
# Fixed Dex LinkedIn handle handling, timeline note/association normalization and stale sync errors.
# Sync-only recovery verified the existing note; repeating stable-key invocation reused the same job/note.
# Final verification: 35 backend tests passed with actual MongoDB; frontend production build passed.
# Cited live findings, paid providers and live field updates remain unverified.

# Collector revision: owner declined paid Dex delegation and requested independent collection.
# Default public discovery + pinned Maigret detector + Trafilatura + FtM schema snapshots implemented.
# Empty runs now return no_results and never write a note; matching usernames remain candidates.
# Live job <PRIVATE_RUN_OR_NOTE_ID>: one unconfirmed account candidate, zero findings,
# search access challenge, LinkedIn robots denial, no cached research, no writeback, zero paid attempts.
# Final checks: 42 backend tests passed with real Mongo and real Maigret detector/synthetic responses;
# frontend build and expanded Chromium fixture smoke passed. Locked collector reinstall/pip check passed.
# Full FtM runtime was not installed; selected MIT schemas adapted to existing Pydantic/Mongo stack.
# First useful cited live enrichment remains incomplete; details in docs/verification.md.

# LinkedIn scraper evaluation, October 7, 2026: isolated joeyism revision b1cdc1c.
# Two upstream model unit tests passed; pip check passed. Offline real-Chromium script
# passed 11 characterization checks (including six confirmed defects), four intercepted
# requests, zero live requests. No real session, Dex mutation, provider charge or integration.
# Regression: 42 backend tests passed with actual MongoDB; frontend build passed.
# Full verdict, license conflict and reproducible script: docs/linkedin-connectors.md.

# Authorized LinkedIn implementation: isolated pinned parser, policy-bound session retrieval,
# permitted HTML import via CLI/API/UI, evidence origin/pending review, durable source checkpoint.
# 64 backend tests passed with actual Mongo and pinned Chromium parser on synthetic HTML;
# production build, repeated isolated install/pip check, fixture CLI and file-upload browser passed.
# Initial failures were corrected: fragment-page challenge detection, test collection/anchor,
# and absent fixture frontend startup. No assertions were disabled.
# The selected contact’s live dry-run job <PRIVATE_RUN_OR_NOTE_ID> returned authentication_required:
# no private LinkedIn session, zero new findings/paid calls/Dex writes. No live enrichment claimed.

# Company-first expansion: bounded candidate domain + published same-host pages; business context
# is explicitly company_context_only, unresolved/pending, never personal identity/affiliation proof.
# 72 backend tests, production build and fixture browser passed; provider-budget failures do not
# poison subsequent cache reads. Existing independent source failures remain isolated.
# The selected contact’s live job <PRIVATE_RUN_OR_NOTE_ID> collected five cited company-context entries.
# Dex note <PRIVATE_RUN_OR_NOTE_ID> content/association verified; no field/link changes.
# Repeat invocation reused the same job/note/counters. Zero paid research attempts.
# Current role, biography and relationships remain unconfirmed; broad person discovery incomplete.

api_anything_integration_2026_10_13:
  implemented: true
  sources: [openalex_authors, europe_pmc_publications, hacker_news_company_mentions]
  worker: "Pinned API Anything 0.1.0 offline request/extraction components; Hugin owns transport and budgets. No cookies, login, browser fallback or auto-heal."
  backend_verification: "82 passed with real Mongo and installed pinned collectors; focused API Anything checks 10 passed."
  frontend_verification: "Production and separate fixture builds passed; fixture Chromium smoke validates pending API publication evidence and integration UI."
  live_verification: "Final selected-contact dry run <PRIVATE_RUN_OR_NOTE_ID>: six public requests, zero paid attempts, no_results, no Dex writes. Three candidate publication/news records were rejected for name/relevance mismatch. Separate public source smoke reads returned usable metadata."
  limitations: "Academic/technical coverage only. No new the selected contact facts; no live API-source note writeback. Fixture writeback is simulated. Additional trade/conference adapters and social access remain deferred. OpenAlex reports a query-cost estimate; account billing unverified."
  editorial: "Humanizer main skill, precision/conservative pass; supplemental surface reference unavailable."
