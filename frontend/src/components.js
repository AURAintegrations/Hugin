import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Menu, 
  X, 
  ChevronDown, 
  Play, 
  Star, 
  Users, 
  Calendar, 
  MessageCircle, 
  BarChart3, 
  TrendingUp, 
  Mail, 
  Phone, 
  Settings, 
  Search, 
  Bell, 
  User, 
  Home, 
  Briefcase, 
  Target, 
  PieChart, 
  FileText, 
  Zap,
  Building,
  Award,
  CheckCircle,
  ArrowRight,
  Globe,
  Smartphone,
  Filter,
  Plus,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';

// Header Component
export const Header = ({ onLoginClick, showLogin = true }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-green-500 rounded-lg flex items-center justify-center mr-2">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">HighLevel</span>
            </div>
          </div>

          <nav className="hidden md:flex space-x-8">
            <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">Features</a>
            <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">Pricing</a>
            <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">Resources</a>
            <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">Support</a>
          </nav>

          <div className="hidden md:flex items-center space-x-4">
            {showLogin && (
              <button 
                onClick={onLoginClick}
                className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
              >
                Login to App
              </button>
            )}
            <button className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors">
              14 DAY FREE TRIAL
            </button>
          </div>

          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-700 hover:text-blue-600"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-white border-t"
          >
            <div className="px-2 pt-2 pb-3 space-y-1">
              <a href="#" className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-blue-600">Features</a>
              <a href="#" className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-blue-600">Pricing</a>
              <a href="#" className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-blue-600">Resources</a>
              <a href="#" className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-blue-600">Support</a>
              {showLogin && (
                <button 
                  onClick={onLoginClick}
                  className="block w-full text-left px-3 py-2 text-base font-medium text-gray-700 hover:text-blue-600"
                >
                  Login to App
                </button>
              )}
              <div className="px-3 py-2">
                <button className="w-full bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors">
                  14 DAY FREE TRIAL
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};

// Hero Section Component
export const HeroSection = () => {
  return (
    <section className="relative bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white overflow-hidden">
      <div className="absolute inset-0 bg-black opacity-50"></div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 items-center gap-12">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="flex items-center mb-6">
              <Zap className="w-6 h-6 text-yellow-400 mr-2" />
              <span className="text-yellow-400 font-semibold">Power Up Your Business:</span>
            </div>
            <h1 className="text-4xl lg:text-6xl font-bold mb-6 leading-tight">
              Elevate Your Marketing and Sales with HighLevel's{' '}
              <span className="text-blue-400">All-in-One Platform!</span>
            </h1>
            <p className="text-xl mb-8 text-gray-300 leading-relaxed">
              Transform your business with our comprehensive CRM, marketing automation, 
              and sales funnel platform designed for agencies and businesses.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all transform hover:scale-105 flex items-center justify-center">
                14 DAY FREE TRIAL
                <span className="ml-2 text-sm">No obligations, no contracts, cancel at any time</span>
              </button>
              <button className="border-2 border-white text-white hover:bg-white hover:text-gray-900 px-8 py-4 rounded-lg text-lg font-semibold transition-all flex items-center justify-center">
                <Play className="w-5 h-5 mr-2" />
                Watch Demo
              </button>
            </div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="relative"
          >
            <img 
              src="https://images.pexels.com/photos/8254894/pexels-photo-8254894.jpeg" 
              alt="HighLevel Dashboard"
              className="rounded-2xl shadow-2xl w-full"
            />
            <div className="absolute inset-0 bg-gradient-to-tr from-blue-500/20 to-green-500/20 rounded-2xl"></div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

// Awards Section Component
export const AwardsSection = () => {
  const awards = [
    { name: "Momentum Leader", year: "2025" },
    { name: "#1 Capterra", year: "2025" },
    { name: "Best Value", year: "2025" },
    { name: "Users Most Likely to Recommend", year: "2025" },
    { name: "Regional Leader", year: "2025" },
    { name: "Grid Leader", year: "2025" }
  ];

  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">AWARDS</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 items-center">
          {awards.map((award, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="text-center"
            >
              <div className="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow">
                <Award className="w-12 h-12 text-orange-500 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 text-sm">{award.name}</h3>
                <p className="text-orange-500 text-xs font-medium">{award.year}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Stats Section Component
export const StatsSection = () => {
  const stats = [
    { number: "1260000", label: "BUSINESSES POWERED", suffix: "" },
    { number: "863100", label: "MONTHLY MESSAGES", suffix: "" },
    { number: "123", label: "MONTHLY LEADS", suffix: "" },
    { number: "12", label: "MONTHLY CONVERSATIONS", suffix: "" }
  ];

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            We're in The Business Of Helping You Grow Your Business
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            HighLevel is the first-ever all-in-one platform that will give you the tools, support and resources you need to succeed and crush your marketing goals. Currently serving:
          </p>
        </div>
        
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="text-center"
            >
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="text-4xl font-bold text-blue-600 mb-2">{stat.number}</div>
                <div className="text-sm font-semibold text-gray-900 uppercase">{stat.label}</div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <img 
            src="https://images.pexels.com/photos/7663144/pexels-photo-7663144.jpeg" 
            alt="Platform Demo"
            className="rounded-2xl shadow-2xl mx-auto max-w-4xl w-full"
          />
        </div>
      </div>
    </section>
  );
};

// Features Section Component
export const FeaturesSection = () => {
  return (
    <section className="py-16 bg-slate-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">
            HighLevel: Everything You Need To Succeed
          </h2>
          <p className="text-xl text-gray-300">
            We help you consolidate all of your marketing tools.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              icon: <Users className="w-8 h-8" />,
              title: "CRM & Pipeline Management",
              description: "Manage leads, track opportunities, and automate your sales process with our powerful CRM system."
            },
            {
              icon: <Calendar className="w-8 h-8" />,
              title: "Appointment Scheduling",
              description: "Let clients book appointments automatically with calendar integration and automated reminders."
            },
            {
              icon: <Mail className="w-8 h-8" />,
              title: "Email Marketing",
              description: "Create and send beautiful email campaigns with advanced automation and segmentation."
            },
            {
              icon: <MessageCircle className="w-8 h-8" />,
              title: "SMS Marketing",
              description: "Reach customers instantly with text message campaigns and automated follow-ups."
            },
            {
              icon: <Globe className="w-8 h-8" />,
              title: "Website & Funnel Builder",
              description: "Build professional websites and sales funnels with our drag-and-drop builder."
            },
            {
              icon: <BarChart3 className="w-8 h-8" />,
              title: "Analytics & Reporting",
              description: "Track performance with detailed analytics and customizable reports."
            }
          ].map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-slate-800 rounded-lg p-6 hover:bg-slate-700 transition-colors"
            >
              <div className="text-blue-400 mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
              <p className="text-gray-300">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Login Component
export const LoginForm = ({ onClose, onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    // Mock login - in real app, this would validate credentials
    if (email && password) {
      onLoginSuccess();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-md"
      >
        <div className="p-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-green-500 rounded-lg flex items-center justify-center mr-2">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">HighLevel</span>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="w-6 h-6" />
            </button>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Sign into your account</h2>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Your email address"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="The password you picked"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <div className="text-right mt-2">
                <a href="#" className="text-sm text-blue-600 hover:text-blue-800">Forgot password?</a>
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold transition-colors"
            >
              Sign in
            </button>

            <div className="text-center text-gray-500 my-4">Or continue with</div>

            <button
              type="button"
              className="w-full border border-gray-300 hover:bg-gray-50 text-gray-700 py-3 rounded-lg font-semibold transition-colors flex items-center justify-center"
            >
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Sign in with Google
            </button>

            <div className="text-center text-sm text-gray-600 mt-4">
              By signing in you agree to our{' '}
              <a href="#" className="text-blue-600 hover:text-blue-800">Terms and Conditions</a>
            </div>
          </form>
        </div>
      </motion.div>
    </div>
  );
};

// Dashboard Sidebar Component
export const DashboardSidebar = ({ activeSection, setActiveSection }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <Home className="w-5 h-5" /> },
    { id: 'contacts', label: 'Contacts', icon: <Users className="w-5 h-5" /> },
    { id: 'conversations', label: 'Conversations', icon: <MessageCircle className="w-5 h-5" /> },
    { id: 'calendar', label: 'Calendar', icon: <Calendar className="w-5 h-5" /> },
    { id: 'campaigns', label: 'Campaigns', icon: <Mail className="w-5 h-5" /> },
    { id: 'funnels', label: 'Funnels', icon: <Target className="w-5 h-5" /> },
    { id: 'websites', label: 'Websites', icon: <Globe className="w-5 h-5" /> },
    { id: 'opportunities', label: 'Opportunities', icon: <Briefcase className="w-5 h-5" /> },
    { id: 'analytics', label: 'Analytics', icon: <BarChart3 className="w-5 h-5" /> },
    { id: 'settings', label: 'Settings', icon: <Settings className="w-5 h-5" /> }
  ];

  return (
    <div className="w-64 bg-slate-900 text-white h-screen fixed left-0 top-0 overflow-y-auto">
      <div className="p-6">
        <div className="flex items-center mb-8">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-green-500 rounded-lg flex items-center justify-center mr-3">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold">HighLevel</span>
        </div>

        <nav className="space-y-2">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveSection(item.id)}
              className={`w-full flex items-center px-4 py-3 rounded-lg text-left transition-colors ${
                activeSection === item.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              {item.icon}
              <span className="ml-3">{item.label}</span>
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
};

// Dashboard Header Component
export const DashboardHeader = ({ onLogout }) => {
  return (
    <header className="bg-white shadow-sm border-b ml-64 sticky top-0 z-40">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Search className="w-5 h-5 text-gray-400 mr-3" />
            <input
              type="text"
              placeholder="Search contacts, campaigns, etc..."
              className="bg-gray-50 border-0 rounded-lg px-4 py-2 w-96 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-center space-x-4">
            <button className="relative p-2 text-gray-600 hover:text-gray-900">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
            </button>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
              <div className="hidden md:block">
                <div className="text-sm font-semibold text-gray-900">John Doe</div>
                <div className="text-xs text-gray-500">Agency Owner</div>
              </div>
              <button
                onClick={onLogout}
                className="text-gray-600 hover:text-gray-900 px-3 py-1 text-sm"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

// Dashboard Overview Component
export const DashboardOverview = () => {
  const stats = [
    { label: 'Total Contacts', value: '2,847', change: '+12%', icon: <Users className="w-8 h-8" /> },
    { label: 'Active Campaigns', value: '23', change: '+5%', icon: <Mail className="w-8 h-8" /> },
    { label: 'Monthly Revenue', value: '$47,892', change: '+23%', icon: <TrendingUp className="w-8 h-8" /> },
    { label: 'Conversion Rate', value: '8.4%', change: '+1.2%', icon: <Target className="w-8 h-8" /> }
  ];

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's what's happening with your business.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-sm border p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-blue-600">{stat.icon}</div>
              <span className="text-green-600 text-sm font-semibold">{stat.change}</span>
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</div>
            <div className="text-sm text-gray-600">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Charts and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Analytics</h3>
          <div className="h-64 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg flex items-center justify-center">
            <img 
              src="https://images.pexels.com/photos/8532850/pexels-photo-8532850.jpeg" 
              alt="Analytics Chart"
              className="w-full h-full object-cover rounded-lg"
            />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {[
              { action: 'New contact added', contact: 'Sarah Johnson', time: '2 min ago' },
              { action: 'Campaign sent', contact: 'Newsletter #47', time: '1 hour ago' },
              { action: 'Appointment booked', contact: 'Mike Chen', time: '3 hours ago' },
              { action: 'Deal closed', contact: '$2,500 - ABC Corp', time: '5 hours ago' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center space-x-3 py-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">{activity.action}</div>
                  <div className="text-xs text-gray-500">{activity.contact}</div>
                </div>
                <div className="text-xs text-gray-400">{activity.time}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Contacts Management Component
export const ContactsManagement = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  
  const mockContacts = [
    { id: 1, name: 'Sarah Johnson', email: 'sarah@email.com', phone: '+1 (555) 123-4567', status: 'Lead', lastContact: '2 hours ago', value: '$2,500' },
    { id: 2, name: 'Mike Chen', email: 'mike@company.com', phone: '+1 (555) 234-5678', status: 'Customer', lastContact: '1 day ago', value: '$5,200' },
    { id: 3, name: 'Emily Davis', email: 'emily@startup.com', phone: '+1 (555) 345-6789', status: 'Prospect', lastContact: '3 days ago', value: '$1,800' },
    { id: 4, name: 'James Wilson', email: 'james@business.com', phone: '+1 (555) 456-7890', status: 'Lead', lastContact: '1 week ago', value: '$3,400' },
    { id: 5, name: 'Lisa Thompson', email: 'lisa@agency.com', phone: '+1 (555) 567-8901', status: 'Customer', lastContact: '2 weeks ago', value: '$7,800' }
  ];

  const filteredContacts = mockContacts.filter(contact =>
    contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contact.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Contacts</h1>
          <p className="text-gray-600">Manage your leads, prospects, and customers</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Add Contact
        </button>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search contacts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Contacts</option>
              <option value="lead">Leads</option>
              <option value="prospect">Prospects</option>
              <option value="customer">Customers</option>
            </select>
          </div>
        </div>
      </div>

      {/* Contacts Table */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact Info</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Contact</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredContacts.map((contact) => (
                <tr key={contact.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{contact.name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{contact.email}</div>
                    <div className="text-sm text-gray-500">{contact.phone}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      contact.status === 'Customer' ? 'bg-green-100 text-green-800' :
                      contact.status === 'Lead' ? 'bg-blue-100 text-blue-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {contact.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {contact.lastContact}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {contact.value}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <button className="text-blue-600 hover:text-blue-900">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="text-gray-600 hover:text-gray-900">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button className="text-red-600 hover:text-red-900">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Default export for easier imports
const Components = {
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
};

export default Components;