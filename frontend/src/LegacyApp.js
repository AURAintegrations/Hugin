import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import './App.css';
import {
  Header,
  HeroSection,
  FeaturesSection,
  LoginForm,
  DashboardSidebar,
  DashboardHeader,
  HuginOverview,
  ConversationsModule,
  ContentBoard,
  ContentCalendar,
  HuginAssistant
} from './components';

// Landing Page Component (Updated for Hugin)
const LandingPage = ({ onLoginClick }) => {
  return (
    <div className="min-h-screen bg-white">
      <Header onLoginClick={onLoginClick} />
      <HeroSection />

      {/* Stats Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Organize Your Digital Life
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Hugin helps content creators, entrepreneurs, and professionals organize their online conversations and content ideas efficiently.
            </p>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { number: "10,000+", label: "Conversations Saved" },
              { number: "5,000+", label: "Content Ideas Organized" },
              { number: "2,500+", label: "Posts Scheduled" },
              { number: "95%", label: "User Satisfaction" }
            ].map((stat, index) => (
              <div key={index} className="text-center">
                <div className="bg-white rounded-lg p-6 shadow-sm">
                  <div className="text-3xl font-bold text-purple-600 mb-2">{stat.number}</div>
                  <div className="text-sm font-semibold text-gray-900">{stat.label}</div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-16 text-center">
            <img
              src="https://images.pexels.com/photos/7663144/pexels-photo-7663144.jpeg"
              alt="Hugin Dashboard"
              className="rounded-2xl shadow-2xl mx-auto max-w-4xl w-full"
            />
          </div>
        </div>
      </section>

      <FeaturesSection />

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-br from-purple-600 to-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Build Your Second Brain?
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join thousands of creators who are already organizing their digital conversations and content with Hugin.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-purple-600 hover:bg-gray-100 px-8 py-4 rounded-lg text-lg font-semibold transition-colors">
              Start Free Trial
            </button>
            <button className="border-2 border-white text-white hover:bg-white hover:text-purple-600 px-8 py-4 rounded-lg text-lg font-semibold transition-colors">
              Schedule Demo
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center mr-2">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <span className="text-xl font-bold">Hugin</span>
              </div>
              <p className="text-gray-400 mb-4">
                Your second brain for organizing conversations and content across all platforms.
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
            <p>&copy; 2025 Hugin. All rights reserved. | Privacy Policy | Terms of Service</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Dashboard Component (Updated for Hugin)
const Dashboard = ({ onLogout }) => {
  const [activeSection, setActiveSection] = useState('overview');

  const renderDashboardContent = () => {
    switch (activeSection) {
      case 'overview':
        return <HuginOverview />;
      case 'conversations':
        return <ConversationsModule />;
      case 'content-board':
        return <ContentBoard />;
      case 'content-calendar':
        return <ContentCalendar />;
      case 'hugin-assistant':
        return <HuginAssistant />;
      case 'settings':
        return (
          <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Settings</h1>
            <div className="bg-white rounded-xl shadow-sm border p-8">
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Account Settings</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Display Name</label>
                      <input type="text" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" defaultValue="Content Creator" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                      <input type="email" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" defaultValue="user@example.com" />
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Platform Connections</h3>
                  <div className="space-y-3">
                    {[
                      { name: 'Instagram', connected: true },
                      { name: 'LinkedIn', connected: true },
                      { name: 'Twitter', connected: false },
                      { name: 'Facebook', connected: false }
                    ].map((platform) => (
                      <div key={platform.name} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                        <span className="font-medium text-gray-900">{platform.name}</span>
                        <button className={`px-3 py-1 rounded text-sm ${platform.connected ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                          {platform.connected ? 'Connected' : 'Connect'}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Notifications</h3>
                  <div className="space-y-3">
                    <label className="flex items-center space-x-3">
                      <input type="checkbox" className="rounded border-gray-300 text-purple-600 focus:ring-purple-500" defaultChecked />
                      <span className="text-gray-700">Email notifications for new content ideas</span>
                    </label>
                    <label className="flex items-center space-x-3">
                      <input type="checkbox" className="rounded border-gray-300 text-purple-600 focus:ring-purple-500" defaultChecked />
                      <span className="text-gray-700">Push notifications for scheduled posts</span>
                    </label>
                    <label className="flex items-center space-x-3">
                      <input type="checkbox" className="rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
                      <span className="text-gray-700">Weekly summary reports</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      default:
        return <HuginOverview />;
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
