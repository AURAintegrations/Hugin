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
  Trash2,
  Brain,
  Columns3,
  CalendarDays,
  Bot,
  Hash,
  Instagram,
  Linkedin,
  Twitter,
  Facebook,
  Send,
  Archive,
  Clock,
  CheckCircle2,
  Circle,
  MoveRight,
  Sparkles,
  MessageSquare,
  Copy,
  Bookmark,
  Tag,
  ChevronRight,
  Download,
  Upload
} from 'lucide-react';

// Header Component (Updated for Hugin)
export const Header = ({ onLoginClick, showLogin = true }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center mr-2">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">Hugin</span>
            </div>
          </div>

          <nav className="hidden md:flex space-x-8">
            <a href="#" className="text-gray-700 hover:text-purple-600 px-3 py-2 text-sm font-medium">Features</a>
            <a href="#" className="text-gray-700 hover:text-purple-600 px-3 py-2 text-sm font-medium">Pricing</a>
            <a href="#" className="text-gray-700 hover:text-purple-600 px-3 py-2 text-sm font-medium">Resources</a>
            <a href="#" className="text-gray-700 hover:text-purple-600 px-3 py-2 text-sm font-medium">Support</a>
          </nav>

          <div className="hidden md:flex items-center space-x-4">
            {showLogin && (
              <button 
                onClick={onLoginClick}
                className="text-gray-700 hover:text-purple-600 px-3 py-2 text-sm font-medium"
              >
                Login to App
              </button>
            )}
            <button className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors">
              Start Free Trial
            </button>
          </div>

          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-700 hover:text-purple-600"
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
              <a href="#" className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-purple-600">Features</a>
              <a href="#" className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-purple-600">Pricing</a>
              <a href="#" className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-purple-600">Resources</a>
              <a href="#" className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-purple-600">Support</a>
              {showLogin && (
                <button 
                  onClick={onLoginClick}
                  className="block w-full text-left px-3 py-2 text-base font-medium text-gray-700 hover:text-purple-600"
                >
                  Login to App
                </button>
              )}
              <div className="px-3 py-2">
                <button className="w-full bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors">
                  Start Free Trial
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};

// Hero Section Component (Updated for Hugin)
export const HeroSection = () => {
  return (
    <section className="relative bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white overflow-hidden">
      <div className="absolute inset-0 bg-black opacity-50"></div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 items-center gap-12">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="flex items-center mb-6">
              <Brain className="w-6 h-6 text-purple-400 mr-2" />
              <span className="text-purple-400 font-semibold">Your Second Brain:</span>
            </div>
            <h1 className="text-4xl lg:text-6xl font-bold mb-6 leading-tight">
              Organize Your{' '}
              <span className="text-purple-400">Digital Conversations</span>
              {' '}& Content Ideas
            </h1>
            <p className="text-xl mb-8 text-gray-300 leading-relaxed">
              Hugin helps you save, organize, and leverage your online conversations and content ideas 
              across Instagram, LinkedIn, and other platforms. Never lose a great conversation or content idea again.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all transform hover:scale-105 flex items-center justify-center">
                <Brain className="w-5 h-5 mr-2" />
                Start Your Second Brain
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
              alt="Hugin Dashboard"
              className="rounded-2xl shadow-2xl w-full"
            />
            <div className="absolute inset-0 bg-gradient-to-tr from-purple-500/20 to-blue-500/20 rounded-2xl"></div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

// Features Section Component (Updated for Hugin)
export const FeaturesSection = () => {
  return (
    <section className="py-16 bg-slate-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">
            Your Complete Content Organization System
          </h2>
          <p className="text-xl text-gray-300">
            Capture, organize, and leverage every conversation and content idea.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              icon: <MessageCircle className="w-8 h-8" />,
              title: "Conversation Manager",
              description: "Save and organize online conversations from Instagram, LinkedIn, and other platforms with tags and status tracking."
            },
            {
              icon: <Columns3 className="w-8 h-8" />,
              title: "Content Board",
              description: "Kanban-style board to manage your content ideas, drafts, and posts across different stages of creation."
            },
            {
              icon: <CalendarDays className="w-8 h-8" />,
              title: "Content Calendar",
              description: "Plan and schedule your content with a visual weekly calendar view and automated reminders."
            },
            {
              icon: <Bot className="w-8 h-8" />,
              title: "AI Assistant",
              description: "Get conversation summaries, content ideas, and retrieve saved items using semantic search."
            },
            {
              icon: <Hash className="w-8 h-8" />,
              title: "Smart Tagging",
              description: "Organize everything with intelligent tags and categories for easy discovery and filtering."
            },
            {
              icon: <BarChart3 className="w-8 h-8" />,
              title: "Content Analytics",
              description: "Track your content creation progress, popular tags, and engagement metrics."
            }
          ].map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-slate-800 rounded-lg p-6 hover:bg-slate-700 transition-colors"
            >
              <div className="text-purple-400 mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
              <p className="text-gray-300">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Login Component (Updated for Hugin)
export const LoginForm = ({ onClose, onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
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
              <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center mr-2">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">Hugin</span>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="w-6 h-6" />
            </button>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Access Your Second Brain</h2>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Your email address"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Your password"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
              <div className="text-right mt-2">
                <a href="#" className="text-sm text-purple-600 hover:text-purple-800">Forgot password?</a>
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 rounded-lg font-semibold transition-colors"
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
          </form>
        </div>
      </motion.div>
    </div>
  );
};

// Dashboard Sidebar Component (Updated for Hugin)
export const DashboardSidebar = ({ activeSection, setActiveSection }) => {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: <Home className="w-5 h-5" /> },
    { id: 'conversations', label: 'Conversations', icon: <MessageCircle className="w-5 h-5" /> },
    { id: 'content-board', label: 'Content Board', icon: <Columns3 className="w-5 h-5" /> },
    { id: 'content-calendar', label: 'Content Calendar', icon: <CalendarDays className="w-5 h-5" /> },
    { id: 'hugin-assistant', label: 'Hugin Assistant', icon: <Bot className="w-5 h-5" /> },
    { id: 'settings', label: 'Settings', icon: <Settings className="w-5 h-5" /> }
  ];

  return (
    <div className="w-64 bg-slate-900 text-white h-screen fixed left-0 top-0 overflow-y-auto">
      <div className="p-6">
        <div className="flex items-center mb-8">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center mr-3">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold">Hugin</span>
        </div>

        <nav className="space-y-2">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveSection(item.id)}
              className={`w-full flex items-center px-4 py-3 rounded-lg text-left transition-colors ${
                activeSection === item.id
                  ? 'bg-purple-600 text-white'
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

// Dashboard Header Component (Updated for Hugin)
export const DashboardHeader = ({ onLogout }) => {
  return (
    <header className="bg-white shadow-sm border-b ml-64 sticky top-0 z-40">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Search className="w-5 h-5 text-gray-400 mr-3" />
            <input
              type="text"
              placeholder="Search conversations, content, tags..."
              className="bg-gray-50 border-0 rounded-lg px-4 py-2 w-96 focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div className="flex items-center space-x-4">
            <button className="relative p-2 text-gray-600 hover:text-gray-900">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-purple-500 rounded-full"></span>
            </button>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
              <div className="hidden md:block">
                <div className="text-sm font-semibold text-gray-900">Content Creator</div>
                <div className="text-xs text-gray-500">Second Brain User</div>
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

// Hugin Overview Component (New Dashboard)
export const HuginOverview = () => {
  const stats = [
    { label: 'Conversations Saved', value: '127', change: '+23 this week', icon: <MessageCircle className="w-8 h-8" /> },
    { label: 'Content Posts', value: '45', change: '+8 this week', icon: <FileText className="w-8 h-8" /> },
    { label: 'Active Tags', value: '18', change: '+3 new tags', icon: <Hash className="w-8 h-8" /> },
    { label: 'Scheduled Posts', value: '12', change: '+5 this week', icon: <Clock className="w-8 h-8" /> }
  ];

  const recentActivity = [
    { action: 'Saved Instagram conversation', contact: '@sarah_marketing', time: '2 min ago', platform: 'instagram' },
    { action: 'Created content draft', contact: 'LinkedIn post about AI', time: '1 hour ago', platform: 'linkedin' },
    { action: 'Tagged conversation', contact: '#content-ideas', time: '3 hours ago', platform: 'general' },
    { action: 'Scheduled post', contact: 'Weekly newsletter', time: '5 hours ago', platform: 'general' }
  ];

  const topTags = [
    { name: 'content-ideas', count: 34 },
    { name: 'networking', count: 28 },
    { name: 'collaboration', count: 22 },
    { name: 'inspiration', count: 19 },
    { name: 'strategy', count: 16 }
  ];

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'instagram': return <Instagram className="w-4 h-4 text-pink-500" />;
      case 'linkedin': return <Linkedin className="w-4 h-4 text-blue-600" />;
      case 'twitter': return <Twitter className="w-4 h-4 text-blue-400" />;
      default: return <MessageCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Second Brain Overview</h1>
        <p className="text-gray-600">Welcome back! Here's what's happening with your content organization.</p>
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
              <div className="text-purple-600">{stat.icon}</div>
              <span className="text-green-600 text-sm font-semibold">{stat.change}</span>
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</div>
            <div className="text-sm text-gray-600">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex items-center space-x-3 py-3 border-b border-gray-100 last:border-b-0">
                <div className="flex-shrink-0">{getPlatformIcon(activity.platform)}</div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">{activity.action}</div>
                  <div className="text-xs text-gray-500">{activity.contact}</div>
                </div>
                <div className="text-xs text-gray-400">{activity.time}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Tags */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Tags</h3>
          <div className="space-y-3">
            {topTags.map((tag, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Hash className="w-4 h-4 text-purple-500" />
                  <span className="text-sm font-medium text-gray-900">{tag.name}</span>
                </div>
                <span className="text-sm text-gray-500">{tag.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Content Analytics */}
      <div className="mt-6 bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Content Analytics</h3>
        <div className="h-64 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg flex items-center justify-center">
          <img 
            src="https://images.pexels.com/photos/8532850/pexels-photo-8532850.jpeg" 
            alt="Content Analytics"
            className="w-full h-full object-cover rounded-lg"
          />
        </div>
      </div>
    </div>
  );
};

// Conversations Module Component (Kanban Board)
export const ConversationsModule = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [selectedTag, setSelectedTag] = useState('');
  const [toastVisible, setToastVisible] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  
  // Kanban columns configuration
  const columns = {
    inbox: { id: 'inbox', title: 'Inbox', color: 'border-t-blue-500' },
    replied: { id: 'replied', title: 'Replied', color: 'border-t-green-500' },
    nurturing: { id: 'nurturing', title: 'Nurturing', color: 'border-t-yellow-500' },
    followUp: { id: 'followUp', title: 'Follow-Up', color: 'border-t-orange-500' },
    archived: { id: 'archived', title: 'Archived', color: 'border-t-gray-500' }
  };

  const [conversations, setConversations] = useState({
    inbox: [
      { 
        id: 'conv-1', 
        contact: '@sarah_marketing', 
        platform: 'instagram', 
        summary: 'Interested in collaboration opportunities and cross-promotion strategies for content creators...', 
        tags: ['collaboration', 'content-ideas', 'networking'], 
        lastInteraction: '2 hours ago',
        priority: 'high'
      },
      { 
        id: 'conv-2', 
        contact: 'Alex Rivera', 
        platform: 'linkedin', 
        summary: 'Asked about my experience with AI tools for content creation and productivity workflows...', 
        tags: ['ai-tools', 'productivity'], 
        lastInteraction: '5 hours ago',
        priority: 'medium'
      }
    ],
    replied: [
      { 
        id: 'conv-3', 
        contact: 'Mike Chen', 
        platform: 'linkedin', 
        summary: 'Responded to questions about AI tools for content creation and shared productivity tips...', 
        tags: ['ai-tools', 'productivity', 'content-creation'], 
        lastInteraction: '1 day ago',
        priority: 'medium'
      },
      { 
        id: 'conv-4', 
        contact: '@creative_jenny', 
        platform: 'instagram', 
        summary: 'Replied to DM about design collaboration and shared portfolio examples...', 
        tags: ['design', 'collaboration'], 
        lastInteraction: '2 days ago',
        priority: 'low'
      }
    ],
    nurturing: [
      { 
        id: 'conv-5', 
        contact: '@emily_design', 
        platform: 'instagram', 
        summary: 'Ongoing design feedback session and potential partnership discussion...', 
        tags: ['design', 'feedback', 'partnership'], 
        lastInteraction: '3 days ago',
        priority: 'high'
      },
      { 
        id: 'conv-6', 
        contact: 'David Park', 
        platform: 'linkedin', 
        summary: 'Building relationship for future collaboration opportunities in tech space...', 
        tags: ['networking', 'tech', 'future-collab'], 
        lastInteraction: '4 days ago',
        priority: 'medium'
      }
    ],
    followUp: [
      { 
        id: 'conv-7', 
        contact: 'Lisa Thompson', 
        platform: 'linkedin', 
        summary: 'Need to follow up on networking conversation about industry trends and events...', 
        tags: ['networking', 'industry-trends', 'events'], 
        lastInteraction: '1 week ago',
        priority: 'medium'
      }
    ],
    archived: [
      { 
        id: 'conv-8', 
        contact: '@james_tech', 
        platform: 'twitter', 
        summary: 'Completed tech discussion about latest development tools and frameworks...', 
        tags: ['tech', 'development', 'tools'], 
        lastInteraction: '2 weeks ago',
        priority: 'low'
      },
      { 
        id: 'conv-9', 
        contact: 'Sofia Martinez', 
        platform: 'linkedin', 
        summary: 'Archived conversation about marketing strategies - project completed...', 
        tags: ['marketing', 'strategy', 'completed'], 
        lastInteraction: '3 weeks ago',
        priority: 'low'
      }
    ]
  });

  // Get all unique platforms and tags for filters
  const allConversations = Object.values(conversations).flat();
  const availablePlatforms = [...new Set(allConversations.map(conv => conv.platform))];
  const availableTags = [...new Set(allConversations.flatMap(conv => conv.tags))];

  // Filter conversations
  const getFilteredConversations = (columnConversations) => {
    return columnConversations.filter(conv => {
      const matchesSearch = conv.contact.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           conv.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           conv.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesPlatform = selectedPlatforms.length === 0 || selectedPlatforms.includes(conv.platform);
      const matchesTag = !selectedTag || conv.tags.includes(selectedTag);
      return matchesSearch && matchesPlatform && matchesTag;
    });
  };

  // Handle platform filter toggle
  const togglePlatform = (platform) => {
    setSelectedPlatforms(prev => 
      prev.includes(platform) 
        ? prev.filter(p => p !== platform)
        : [...prev, platform]
    );
  };

  // Drag and drop handlers
  const handleDragStart = (e, conversationId, sourceColumn) => {
    e.dataTransfer.setData('text/plain', JSON.stringify({ conversationId, sourceColumn }));
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, targetColumn) => {
    e.preventDefault();
    const data = JSON.parse(e.dataTransfer.getData('text/plain'));
    const { conversationId, sourceColumn } = data;

    if (sourceColumn === targetColumn) return;

    // Find the conversation to move
    const conversationToMove = conversations[sourceColumn].find(conv => conv.id === conversationId);
    if (!conversationToMove) return;

    // Update conversations state
    setConversations(prev => ({
      ...prev,
      [sourceColumn]: prev[sourceColumn].filter(conv => conv.id !== conversationId),
      [targetColumn]: [...prev[targetColumn], conversationToMove]
    }));

    // Show success toast
    showToast(`Moved "${conversationToMove.contact}" to ${columns[targetColumn].title}`);
  };

  // Toast notification
  const showToast = (message) => {
    setToastMessage(message);
    setToastVisible(true);
    setTimeout(() => setToastVisible(false), 3000);
  };

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'instagram': return <Instagram className="w-4 h-4 text-pink-500" />;
      case 'linkedin': return <Linkedin className="w-4 h-4 text-blue-600" />;
      case 'twitter': return <Twitter className="w-4 h-4 text-blue-400" />;
      case 'facebook': return <Facebook className="w-4 h-4 text-blue-600" />;
      default: return <MessageCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getTagColor = (tag) => {
    const colors = [
      'bg-purple-100 text-purple-700',
      'bg-blue-100 text-blue-700',
      'bg-green-100 text-green-700',
      'bg-yellow-100 text-yellow-700',
      'bg-pink-100 text-pink-700',
      'bg-indigo-100 text-indigo-700'
    ];
    const index = tag.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[index % colors.length];
  };

  const ConversationCard = ({ conversation, columnId }) => (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.2 }}
      draggable
      onDragStart={(e) => handleDragStart(e, conversation.id, columnId)}
      className="bg-white rounded-lg shadow-sm border p-4 mb-3 hover:shadow-md transition-all cursor-move hover:scale-105"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          {getPlatformIcon(conversation.platform)}
          <span className="font-semibold text-gray-900 text-sm">{conversation.contact}</span>
        </div>
        <div className="flex items-center space-x-1">
          <button className="text-gray-400 hover:text-gray-600 p-1">
            <Eye className="w-3 h-3" />
          </button>
          <button className="text-gray-400 hover:text-gray-600 p-1">
            <MoreHorizontal className="w-3 h-3" />
          </button>
        </div>
      </div>
      
      <p className="text-gray-600 text-xs mb-3 line-clamp-2">
        {conversation.summary}
      </p>
      
      <div className="flex flex-wrap gap-1 mb-2">
        {conversation.tags.slice(0, 2).map((tag, index) => (
          <span key={index} className={`px-2 py-1 text-xs rounded-full ${getTagColor(tag)}`}>
            #{tag}
          </span>
        ))}
        {conversation.tags.length > 2 && (
          <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600">
            +{conversation.tags.length - 2}
          </span>
        )}
      </div>
      
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>{conversation.lastInteraction}</span>
        <div className={`w-2 h-2 rounded-full ${
          conversation.priority === 'high' ? 'bg-red-400' :
          conversation.priority === 'medium' ? 'bg-yellow-400' : 'bg-green-400'
        }`}></div>
      </div>
    </motion.div>
  );

  return (
    <div className="p-6">
      {/* Toast Notification */}
      <AnimatePresence>
        {toastVisible && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50"
          >
            <CheckCircle2 className="w-4 h-4 inline mr-2" />
            {toastMessage}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Conversations</h1>
          <p className="text-gray-600">Track and organize your social media conversations</p>
        </div>
        <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Add Conversation
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          {/* Platform Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Platforms</label>
            <div className="flex flex-wrap gap-2">
              {availablePlatforms.map(platform => (
                <button
                  key={platform}
                  onClick={() => togglePlatform(platform)}
                  className={`flex items-center space-x-1 px-3 py-1 rounded-full text-sm transition-colors ${
                    selectedPlatforms.includes(platform)
                      ? 'bg-purple-100 text-purple-700 border border-purple-300'
                      : 'bg-gray-100 text-gray-600 border border-gray-300 hover:bg-gray-200'
                  }`}
                >
                  {getPlatformIcon(platform)}
                  <span className="capitalize">{platform}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Tag Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Filter by Tag</label>
            <select
              value={selectedTag}
              onChange={(e) => setSelectedTag(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500"
            >
              <option value="">All Tags</option>
              {availableTags.map(tag => (
                <option key={tag} value={tag}>#{tag}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 overflow-x-auto min-h-96">
        {Object.entries(columns).map(([columnId, column]) => {
          const columnConversations = getFilteredConversations(conversations[columnId]);
          
          return (
            <div
              key={columnId}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, columnId)}
              className={`bg-gray-50 rounded-lg p-4 min-h-96 border-t-4 ${column.color}`}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">{column.title}</h3>
                <span className="text-sm text-gray-500 bg-white px-2 py-1 rounded-full">
                  {columnConversations.length}
                </span>
              </div>
              
              <div className="space-y-2">
                <AnimatePresence>
                  {columnConversations.map((conversation) => (
                    <ConversationCard 
                      key={conversation.id} 
                      conversation={conversation} 
                      columnId={columnId}
                    />
                  ))}
                </AnimatePresence>
              </div>
              
              {columnConversations.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <MessageCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No conversations</p>
                </div>
              )}
              
              <button className="w-full mt-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-purple-300 hover:text-purple-600 transition-colors text-sm">
                + Drop here
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Content Board Component (Kanban View)
export const ContentBoard = () => {
  const [columns, setColumns] = useState({
    ideas: {
      title: 'Ideas',
      items: [
        { id: '1', title: 'AI productivity tips', platform: 'linkedin', tags: ['ai', 'productivity'] },
        { id: '2', title: 'Instagram story series', platform: 'instagram', tags: ['stories', 'series'] },
        { id: '3', title: 'Twitter thread on creativity', platform: 'twitter', tags: ['creativity', 'thread'] }
      ]
    },
    drafting: {
      title: 'Drafting',
      items: [
        { id: '4', title: 'LinkedIn post about networking', platform: 'linkedin', tags: ['networking', 'career'] },
        { id: '5', title: 'Instagram carousel design', platform: 'instagram', tags: ['design', 'carousel'] }
      ]
    },
    review: {
      title: 'Review',
      items: [
        { id: '6', title: 'Blog post about content creation', platform: 'blog', tags: ['content', 'creation'] }
      ]
    },
    scheduled: {
      title: 'Scheduled',
      items: [
        { id: '7', title: 'Weekly newsletter', platform: 'email', tags: ['newsletter', 'weekly'] },
        { id: '8', title: 'Instagram Reel', platform: 'instagram', tags: ['reel', 'video'] }
      ]
    },
    published: {
      title: 'Published',
      items: [
        { id: '9', title: 'LinkedIn article', platform: 'linkedin', tags: ['article', 'long-form'] },
        { id: '10', title: 'Twitter poll', platform: 'twitter', tags: ['poll', 'engagement'] }
      ]
    }
  });

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'instagram': return <Instagram className="w-4 h-4 text-pink-500" />;
      case 'linkedin': return <Linkedin className="w-4 h-4 text-blue-600" />;
      case 'twitter': return <Twitter className="w-4 h-4 text-blue-400" />;
      case 'facebook': return <Facebook className="w-4 h-4 text-blue-600" />;
      case 'email': return <Mail className="w-4 h-4 text-green-500" />;
      case 'blog': return <FileText className="w-4 h-4 text-gray-600" />;
      default: return <MessageCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getColumnColor = (columnId) => {
    const colors = {
      ideas: 'border-t-blue-500',
      drafting: 'border-t-yellow-500',
      review: 'border-t-orange-500',
      scheduled: 'border-t-green-500',
      published: 'border-t-purple-500'
    };
    return colors[columnId] || 'border-t-gray-500';
  };

  const ContentCard = ({ item }) => (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      className="bg-white rounded-lg shadow-sm border p-4 mb-3 hover:shadow-md transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between mb-3">
        <h4 className="font-medium text-gray-900 text-sm">{item.title}</h4>
        <div className="flex items-center space-x-1">
          {getPlatformIcon(item.platform)}
          <button className="text-gray-400 hover:text-gray-600">
            <MoreHorizontal className="w-4 h-4" />
          </button>
        </div>
      </div>
      <div className="flex flex-wrap gap-1">
        {item.tags.map((tag, index) => (
          <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
            #{tag}
          </span>
        ))}
      </div>
    </motion.div>
  );

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Content Board</h1>
          <p className="text-gray-600">Manage your content across different stages of creation</p>
        </div>
        <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Add Content
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 overflow-x-auto">
        {Object.entries(columns).map(([columnId, column]) => (
          <div key={columnId} className={`bg-gray-50 rounded-lg p-4 min-h-96 border-t-4 ${getColumnColor(columnId)}`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">{column.title}</h3>
              <span className="text-sm text-gray-500 bg-white px-2 py-1 rounded">
                {column.items.length}
              </span>
            </div>
            <div className="space-y-2">
              <AnimatePresence>
                {column.items.map((item) => (
                  <ContentCard key={item.id} item={item} />
                ))}
              </AnimatePresence>
            </div>
            <button className="w-full mt-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-purple-300 hover:text-purple-600 transition-colors">
              + Add item
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

// Content Calendar Component
export const ContentCalendar = () => {
  const [currentWeek, setCurrentWeek] = useState(new Date());
  
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const weekDates = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(currentWeek);
    date.setDate(date.getDate() - date.getDay() + i);
    return date;
  });

  const mockScheduledContent = {
    '2025-06-22': [
      { id: 1, title: 'LinkedIn post', platform: 'linkedin', time: '09:00', status: 'scheduled' },
      { id: 2, title: 'Instagram story', platform: 'instagram', time: '15:00', status: 'draft' }
    ],
    '2025-06-24': [
      { id: 3, title: 'Twitter thread', platform: 'twitter', time: '12:00', status: 'scheduled' }
    ],
    '2025-06-26': [
      { id: 4, title: 'Newsletter', platform: 'email', time: '10:00', status: 'scheduled' },
      { id: 5, title: 'Instagram Reel', platform: 'instagram', time: '18:00', status: 'idea' }
    ]
  };

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'instagram': return <Instagram className="w-3 h-3 text-pink-500" />;
      case 'linkedin': return <Linkedin className="w-3 h-3 text-blue-600" />;
      case 'twitter': return <Twitter className="w-3 h-3 text-blue-400" />;
      case 'email': return <Mail className="w-3 h-3 text-green-500" />;
      default: return <MessageCircle className="w-3 h-3 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled': return 'bg-green-100 text-green-800 border-green-200';
      case 'draft': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'idea': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Content Calendar</h1>
          <p className="text-gray-600">Plan and schedule your content across platforms</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <button 
              onClick={() => setCurrentWeek(new Date(currentWeek.getTime() - 7 * 24 * 60 * 60 * 1000))}
              className="p-2 text-gray-600 hover:text-gray-900"
            >
              <ChevronDown className="w-4 h-4 rotate-90" />
            </button>
            <span className="font-medium text-gray-900">
              {weekDates[0].toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - {weekDates[6].toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            </span>
            <button 
              onClick={() => setCurrentWeek(new Date(currentWeek.getTime() + 7 * 24 * 60 * 60 * 1000))}
              className="p-2 text-gray-600 hover:text-gray-900"
            >
              <ChevronDown className="w-4 h-4 -rotate-90" />
            </button>
          </div>
          <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center">
            <Plus className="w-4 h-4 mr-2" />
            Add Content
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="grid grid-cols-7 border-b border-gray-200">
          {days.map((day, index) => (
            <div key={day} className="p-4 text-center border-r border-gray-200 last:border-r-0">
              <div className="font-semibold text-gray-900">{day}</div>
              <div className="text-sm text-gray-500 mt-1">
                {weekDates[index].getDate()}
              </div>
            </div>
          ))}
        </div>
        
        <div className="grid grid-cols-7 min-h-96">
          {weekDates.map((date, index) => {
            const dateStr = date.toISOString().split('T')[0];
            const dayContent = mockScheduledContent[dateStr] || [];
            
            return (
              <div key={index} className="p-3 border-r border-gray-200 last:border-r-0 min-h-full">
                <div className="space-y-2">
                  {dayContent.map((content) => (
                    <motion.div
                      key={content.id}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className={`p-2 rounded-lg border text-xs ${getStatusColor(content.status)}`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium truncate">{content.title}</span>
                        {getPlatformIcon(content.platform)}
                      </div>
                      <div className="text-xs opacity-75">{content.time}</div>
                    </motion.div>
                  ))}
                </div>
                <button className="w-full mt-2 py-2 border-2 border-dashed border-gray-200 rounded-lg text-gray-400 hover:border-purple-300 hover:text-purple-600 transition-colors text-xs">
                  + Add
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// Hugin Assistant Component (AI Chat)
export const HuginAssistant = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: "Hello! I'm Hugin, your second brain assistant. I can help you summarize conversations, generate content ideas, and search through your saved items. What would you like to do?",
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const quickActions = [
    { 
      id: 'summarize', 
      title: 'Summarize Conversation', 
      description: 'Paste a conversation and get a summary',
      icon: <MessageSquare className="w-5 h-5" />
    },
    { 
      id: 'content-ideas', 
      title: 'Generate Content Ideas', 
      description: 'Get 3 post ideas based on a theme',
      icon: <Sparkles className="w-5 h-5" />
    },
    { 
      id: 'search', 
      title: 'Search Saved Items', 
      description: 'Find your saved conversations and content',
      icon: <Search className="w-5 h-5" />
    }
  ];

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const newMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages([...messages, newMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        type: 'assistant',
        content: getAIResponse(inputMessage),
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const getAIResponse = (message) => {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('summarize') || lowerMessage.includes('summary')) {
      return "I'd be happy to help summarize a conversation! Please paste the conversation text, and I'll provide a concise summary with key points and actionable insights.";
    } else if (lowerMessage.includes('content ideas') || lowerMessage.includes('post ideas')) {
      return "Great! I can generate content ideas for you. Here are 3 post ideas based on productivity:\n\n1. **'5-Minute Morning Routine'** - Quick tips for starting the day productively\n2. **'Digital Declutter Challenge'** - Weekly challenge to organize digital workspace\n3. **'Productivity Myth Busting'** - Debunking common productivity misconceptions\n\nWould you like ideas for a specific theme or platform?";
    } else if (lowerMessage.includes('search') || lowerMessage.includes('find')) {
      return "I can help you search through your saved items! Here are some recent matches:\n\n• **Instagram conversation** with @sarah_marketing about collaboration (tagged: #networking)\n• **LinkedIn post draft** about AI tools (tagged: #ai-tools, #productivity)\n• **Content idea** for weekly newsletter (tagged: #newsletter)\n\nWhat specific topic or tag are you looking for?";
    } else {
      return "I understand you're looking for help with your content organization. I can assist with:\n\n• **Summarizing conversations** - Paste any conversation for a quick summary\n• **Generating content ideas** - Get tailored suggestions for any platform\n• **Searching saved items** - Find specific conversations or content by keywords\n\nWhat would you like to explore?";
    }
  };

  const handleQuickAction = (actionId) => {
    const actions = {
      'summarize': "I'd like to summarize a conversation",
      'content-ideas': "Can you give me 3 content ideas for LinkedIn?",
      'search': "Help me search through my saved conversations"
    };
    
    setInputMessage(actions[actionId]);
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Hugin Assistant</h1>
          <p className="text-gray-600">Your AI-powered content and conversation assistant</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span className="text-sm text-gray-600">Online</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            {quickActions.map((action) => (
              <button
                key={action.id}
                onClick={() => handleQuickAction(action.id)}
                className="w-full p-4 text-left rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div className="text-purple-600">{action.icon}</div>
                  <div>
                    <div className="font-medium text-gray-900">{action.title}</div>
                    <div className="text-sm text-gray-500">{action.description}</div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Chat Interface */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border flex flex-col h-96">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="font-semibold text-gray-900">Hugin Assistant</div>
                <div className="text-sm text-gray-500">AI-powered helper</div>
              </div>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                  <div className={`text-xs mt-1 ${message.type === 'user' ? 'text-purple-200' : 'text-gray-500'}`}>
                    {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask Hugin anything..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim()}
                className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Default export for easier imports
const Components = {
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
};

export default Components;