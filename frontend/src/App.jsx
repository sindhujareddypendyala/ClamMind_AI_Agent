import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, ArrowRight } from 'lucide-react';
import { authAPI } from './services/api';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import Dashboard from './components/Dashboard';
import MoodTracker from './components/MoodTracker';
import Planner from './components/Planner';
import Exercises from './components/Exercises';
import Prediction from './components/Prediction';
import Favorites from './components/Favorites';
import Settings from './components/Settings';
import ExportData from './components/ExportData';

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showProfileForm, setShowProfileForm] = useState(false);
  const [activePage, setActivePage] = useState('chat'); // 'chat', 'planner', 'tracker', 'exercises', 'prediction', 'favorites', 'profile', 'export'
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Profile Form state
  const [name, setName] = useState('');
  const [age, setAge] = useState(20);
  const [occupation, setOccupation] = useState('');
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    checkUserProfile();
  }, []);

  const checkUserProfile = async () => {
    try {
      setLoading(true);
      const data = await authAPI.getProfile();
      if (data.logged_in) {
        setUser(data.user);
        localStorage.setItem('calmmind_user', JSON.stringify(data.user));
      } else {
        localStorage.removeItem('calmmind_user');
      }
    } catch (err) {
      console.error('Error fetching profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setFormError('Please enter your name.');
      return;
    }

    setSubmitting(true);
    setFormError('');

    try {
      const data = await authAPI.saveProfile({
        name: name.trim(),
        age: parseInt(age),
        occupation: occupation.trim()
      });
      if (data.status === 'success') {
        setUser(data.user);
        localStorage.setItem('calmmind_user', JSON.stringify(data.user));
        setShowProfileForm(false);
        setActivePage('chat');
      }
    } catch (err) {
      console.error('Error creating profile:', err);
      setFormError('Failed to save profile. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('calmmind_user');
    setUser(null);
    setCurrentConversationId(null);
    setActivePage('chat');
    setShowProfileForm(false);
    setName('');
    setAge(20);
    setOccupation('');
  };

  const renderActivePage = () => {
    switch (activePage) {
      case 'chat':
        return (
          <ChatArea 
            user={user} 
            currentConversationId={currentConversationId}
            setCurrentConversationId={setCurrentConversationId}
            setRefreshTrigger={setRefreshTrigger}
            setActivePage={setActivePage}
          />
        );
      case 'planner':
        return <Planner user={user} setRefreshTrigger={setRefreshTrigger} />;
      case 'tracker':
        return <MoodTracker user={user} setActivePage={setActivePage} />;
      case 'exercises':
        return <Exercises />;
      case 'prediction':
        return <Prediction user={user} />;
      case 'favorites':
        return <Favorites />;
      case 'profile':
        return <Settings user={user} setUser={setUser} onLogout={handleLogout} />;
      case 'export':
        return <ExportData user={user} />;
      default:
        return (
          <Dashboard 
            user={user} 
            setActivePage={setActivePage} 
            setRefreshTrigger={setRefreshTrigger}
          />
        );
    }
  };

  // -------------------------------------------------------------
  // APP LOAD LOADING SPLASH
  // -------------------------------------------------------------
  if (loading) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center bg-wellnessBg text-gray-500 gap-3 select-none">
        <Loader2 className="animate-spin text-primaryGreen" size={36} />
        <p className="text-sm font-medium">Starting CalmMind AI...</p>
      </div>
    );
  }

  // -------------------------------------------------------------
  // LANDING PAGE & ONBOARDING (IF NO USER PROFILE EXISTS)
  // -------------------------------------------------------------
  if (!user) {
    if (!showProfileForm) {
      // Landing Page View
      return (
        <div className="h-screen w-screen bg-wellnessBg overflow-y-auto flex items-center justify-center p-6 md:p-12">
          <motion.div 
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-12 gap-8 items-center"
          >
            {/* Left Column content */}
            <div className="md:col-span-7 space-y-6 text-left">
              <div className="text-4xl md:text-5xl font-serif text-primaryGreen font-bold flex items-center gap-2">
                <span>🧠</span> CalmMind AI
              </div>
              <h2 className="text-2xl md:text-3xl font-serif text-darkGreen font-semibold">
                Your Personal Mental Wellness Companion
              </h2>
              <p className="text-gray-600 text-sm md:text-base leading-relaxed">
                CalmMind AI helps users manage stress, anxiety, overthinking, emotional wellness, motivation, and daily wellbeing through AI-powered conversations and personalized wellness recommendations.
              </p>
              
              <div className="pt-4">
                <button
                  onClick={() => setShowProfileForm(true)}
                  className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-primaryGreen text-white font-semibold text-base hover:bg-darkGreen transition-all shadow-lg hover:shadow-xl hover:translate-y-[-1px]"
                >
                  🚀 Start Chat
                </button>
              </div>
            </div>

            {/* Right Column Illustration */}
            <div className="md:col-span-5 flex justify-center">
              <div className="relative w-80 h-80 rounded-3xl bg-white border border-borderGreen/60 p-6 flex flex-col items-center justify-center text-center shadow-xl overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-tr from-lightGreen/50 to-white -z-10" />
                <span className="text-7xl mb-4">🌿</span>
                <h3 className="text-xl font-serif text-darkGreen font-bold">Safe & Private</h3>
                <p className="text-xs text-gray-400 max-w-[200px] mt-2 leading-relaxed">
                  Reflect on daily goals, chat securely, and calm your mind.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      );
    } else {
      // Onboarding profile form view
      return (
        <div className="h-screen w-screen bg-wellnessBg overflow-y-auto flex items-center justify-center p-6">
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-md p-8 rounded-3xl bg-white border border-borderGreen/50 shadow-2xl text-center"
          >
            <div className="mb-6">
              <span className="text-4xl">🌿</span>
              <h2 className="text-2xl font-serif text-darkGreen font-bold mt-2">Create Your Profile</h2>
              <p className="text-xs text-gray-400 mt-1">Customize your experience on CalmMind AI</p>
            </div>

            <form onSubmit={handleProfileSubmit} className="space-y-4 text-left">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-500 uppercase">Full Name</label>
                <input
                  type="text" value={name} onChange={(e) => setName(e.target.value)}
                  placeholder="Enter your full name"
                  className="w-full bg-wellnessBg border border-borderGreen/60 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primaryGreen text-gray-800"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-500 uppercase">Age</label>
                <input
                  type="number" value={age} onChange={(e) => setAge(parseInt(e.target.value) || 0)}
                  className="w-full bg-wellnessBg border border-borderGreen/60 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primaryGreen text-gray-800"
                  min="1" max="120"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-500 uppercase">Occupation</label>
                <input
                  type="text" value={occupation} onChange={(e) => setOccupation(e.target.value)}
                  placeholder="e.g. Student, Software Developer"
                  className="w-full bg-wellnessBg border border-borderGreen/60 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primaryGreen text-gray-800"
                />
              </div>

              {formError && (
                <p className="text-red-500 text-xs mt-1 text-center font-medium">⚠️ {formError}</p>
              )}

              <button
                type="submit" disabled={submitting}
                className="w-full py-3.5 rounded-xl bg-primaryGreen text-white font-medium hover:bg-darkGreen transition-all shadow-md flex items-center justify-center gap-1.5"
              >
                {submitting ? <Loader2 size={16} className="animate-spin" /> : null}
                Continue to CalmMind <ArrowRight size={16} />
              </button>
            </form>
          </motion.div>
        </div>
      );
    }
  }

  // -------------------------------------------------------------
  // MAIN WORKSPACE INTERFACE (LOGGED IN USER)
  // -------------------------------------------------------------
  return (
    <div className="h-screen w-screen flex flex-col md:flex-row overflow-hidden bg-wellnessBg">
      <Sidebar 
        user={user} 
        activePage={activePage} 
        setActivePage={setActivePage}
        currentConversationId={currentConversationId}
        setCurrentConversationId={setCurrentConversationId}
        onLogout={handleLogout}
        refreshTrigger={refreshTrigger}
        setRefreshTrigger={setRefreshTrigger}
      />
      
      {/* Content Canvas */}
      <main className="flex-1 h-full overflow-hidden relative">
        {renderActivePage()}
      </main>
    </div>
  );
}
