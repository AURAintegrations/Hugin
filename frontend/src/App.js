import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import './App.css';
import {
  Header,
  HeroSection,
  AwardsSection,
  StatsSection,
  FeaturesSection,
  LoginForm,
  DashboardSidebar,
  DashboardHeader,
  DashboardOverview,
  ContactsManagement
} from './components';

// Landing Page Component
const LandingPage = ({ onLoginClick }) => {
  return (
    <div className="min-h-screen bg-white">
      <Header onLoginClick={onLoginClick} />
      <HeroSection />
      <AwardsSection />
      <StatsSection />
      <FeaturesSection />
      
      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-green-500 rounded-lg flex items-center justify-center mr-2">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                  </svg>
                </div>
                <span className="text-xl font-bold">HighLevel</span>
              </div>
              <p className="text-gray-400 mb-4">
                The complete marketing automation platform for agencies and businesses.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-white">Pricing</a></li>
                <li><a href="#" className="hover:text-white">Integrations</a></li>
                <li><a href="#" className="hover:text-white">API</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-white">Careers</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Help Center</a></li>
                <li><a href="#" className="hover:text-white">Documentation</a></li>
                <li><a href="#" className="hover:text-white">Community</a></li>
                <li><a href="#" className="hover:text-white">Status</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 HighLevel. All rights reserved. | Privacy Policy | Terms of Service</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Dashboard Component
const Dashboard = ({ onLogout }) => {
  const [activeSection, setActiveSection] = useState('dashboard');

  const renderDashboardContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <DashboardOverview />;
      case 'contacts':
        return <ContactsManagement />;
      case 'conversations':
        return (
          <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Conversations</h1>
            <div className="bg-white rounded-xl shadow-sm border p-8 text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No conversations yet</h3>
              <p className="text-gray-600">Start engaging with your contacts to see conversations here.</p>
            </div>
          </div>
        );
      case 'calendar':
        return (
          <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Calendar</h1>
            <div className="bg-white rounded-xl shadow-sm border p-8">
              <div className="grid grid-cols-7 gap-4 mb-6">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                  <div key={day} className="text-center font-semibold text-gray-700 p-2">
                    {day}
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-7 gap-4">
                {Array.from({ length: 35 }, (_, i) => (
                  <div key={i} className="h-20 border border-gray-200 rounded-lg p-2 hover:bg-gray-50">
                    <div className="text-sm text-gray-600">{((i % 31) + 1)}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      case 'campaigns':
        return (
          <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Campaigns</h1>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { name: 'Welcome Series', type: 'Email', status: 'Active', sent: '1,234' },
                { name: 'Follow-up SMS', type: 'SMS', status: 'Paused', sent: '856' },
                { name: 'Newsletter', type: 'Email', status: 'Active', sent: '2,105' }
              ].map((campaign, index) => (
                <div key={index} className="bg-white rounded-xl shadow-sm border p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">{campaign.name}</h3>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      campaign.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {campaign.status}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">Type: {campaign.type}</div>
                  <div className="text-sm text-gray-600">Sent: {campaign.sent}</div>
                </div>
              ))}
            </div>
          </div>
        );
      default:
        return (
          <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">{activeSection.charAt(0).toUpperCase() + activeSection.slice(1)}</h1>
            <div className="bg-white rounded-xl shadow-sm border p-8 text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Coming Soon</h3>
              <p className="text-gray-600">This feature is under development.</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardSidebar activeSection={activeSection} setActiveSection={setActiveSection} />
      <div className="ml-64">
        <DashboardHeader onLogout={onLogout} />
        <main className="min-h-screen">
          {renderDashboardContent()}
        </main>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [showLogin, setShowLogin] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLoginClick = () => {
    setShowLogin(true);
  };

  const handleLoginClose = () => {
    setShowLogin(false);
  };

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
    setShowLogin(false);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            isLoggedIn ? (
              <Dashboard onLogout={handleLogout} />
            ) : (
              <>
                <LandingPage onLoginClick={handleLoginClick} />
                <AnimatePresence>
                  {showLogin && (
                    <LoginForm 
                      onClose={handleLoginClose} 
                      onLoginSuccess={handleLoginSuccess} 
                    />
                  )}
                </AnimatePresence>
              </>
            )
          } />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;