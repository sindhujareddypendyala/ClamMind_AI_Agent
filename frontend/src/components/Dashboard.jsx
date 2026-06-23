import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Smile, Flame, Battery, Brain, Sparkles, Wind, BookOpen, ChevronRight, Activity, Calendar
} from 'lucide-react';
import { moodAPI, plansAPI } from '../services/api';

export default function Dashboard({ user, setActivePage, setRefreshTrigger }) {
  const [analytics, setAnalytics] = useState({
    average_stress: 0,
    average_anxiety: 0,
    average_energy: 0,
    average_sleep: 0,
    wellness_score: 0
  });
  const [activePlans, setActivePlans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const moodData = await moodAPI.getMoodLogs(7);
      if (moodData.analytics) {
        setAnalytics(moodData.analytics);
      }
      
      const plansData = await plansAPI.getPlans();
      // Filter plans that are not completed (progress < 100)
      setActivePlans(plansData.filter(p => p.completed === 0).slice(0, 2));
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const quickActions = [
    {
      title: 'Guided Breathing',
      desc: 'Soothe your mind with a 16s box breathing exercise.',
      icon: Wind,
      color: 'bg-blue-500/10 text-blue-600 border-blue-100',
      action: () => setActivePage('exercises'),
    },
    {
      title: 'Log Today\'s Mood',
      desc: 'Check in with your feelings to notice trends.',
      icon: Smile,
      color: 'bg-primaryGreen/10 text-primaryGreen border-lightGreen',
      action: () => setActivePage('tracker'),
    },
    {
      title: 'Generate Wellness Plan',
      desc: 'Create actionable tasks targeting anxiety or stress.',
      icon: Calendar,
      color: 'bg-amber-500/10 text-amber-600 border-amber-100',
      action: () => setActivePage('planner'),
    },
    {
      title: 'Predict Mood Outlook',
      desc: 'See how sleep and stress will impact your mood.',
      icon: Sparkles,
      color: 'bg-purple-500/10 text-purple-600 border-purple-100',
      action: () => setActivePage('prediction'),
    },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="p-6 md:p-8 space-y-8 max-w-6xl mx-auto overflow-y-auto h-full pb-16"
    >
      {/* Hero Welcome Row */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-white/60 backdrop-blur-md border border-borderGreen/40 rounded-3xl p-6 md:p-8 shadow-sm">
        <div>
          <h2 className="text-3xl md:text-4xl font-serif text-darkGreen font-bold mb-2">
            {getGreeting()}, {user?.name || 'Friend'} 🌿
          </h2>
          <p className="text-gray-600 text-sm md:text-base">
            Your personal mental wellness companion is here. How is your day going?
          </p>
        </div>
        <button
          onClick={() => setActivePage('chat')}
          className="flex items-center justify-center gap-2 px-6 py-3 rounded-2xl bg-primaryGreen text-white font-medium hover:bg-darkGreen transition-all shadow-md self-start md:self-auto"
        >
          Talk to Companion <ChevronRight size={16} />
        </button>
      </div>

      {/* Wellness Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Wellness Score Card */}
        <div className="md:col-span-1 rounded-3xl bg-white border border-borderGreen/50 p-6 flex flex-col items-center justify-center text-center shadow-xs">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-accentGreen mb-4">Wellness Score</h3>
          <div className="relative w-36 h-36 flex items-center justify-center">
            {/* Visual Circular Progress bar background */}
            <svg className="absolute w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="42" stroke="#EBF0E4" strokeWidth="8" fill="transparent" />
              <circle 
                cx="50" cy="50" r="42" stroke="#2E8B57" strokeWidth="8" fill="transparent" 
                strokeDasharray="264" 
                strokeDashoffset={264 - (264 * (analytics.wellness_score || 70)) / 100}
                strokeLinecap="round"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="text-center">
              <span className="text-4xl font-bold font-serif text-darkGreen">{analytics.wellness_score || 0}</span>
              <span className="text-gray-400 text-xs block">out of 100</span>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-4 leading-relaxed max-w-[200px]">
            Based on your stress, anxiety, sleep, and energy levels this week.
          </p>
        </div>

        {/* Quick Stats Grid */}
        <div className="md:col-span-2 grid grid-cols-2 gap-4">
          <div className="bg-white border border-borderGreen/50 rounded-2xl p-5 flex items-start gap-4">
            <div className="p-3 bg-red-50 text-red-500 rounded-xl">
              <Activity size={20} />
            </div>
            <div>
              <p className="text-xs text-gray-400 font-semibold uppercase">Stress Level</p>
              <h4 className="text-2xl font-bold text-darkGreen mt-1">{analytics.average_stress || 0} <span className="text-xs font-normal text-gray-400">/ 10</span></h4>
              <p className="text-[11px] text-gray-500 mt-1">Average stress level this week</p>
            </div>
          </div>

          <div className="bg-white border border-borderGreen/50 rounded-2xl p-5 flex items-start gap-4">
            <div className="p-3 bg-blue-50 text-blue-500 rounded-xl">
              <Activity size={20} />
            </div>
            <div>
              <p className="text-xs text-gray-400 font-semibold uppercase">Anxiety Level</p>
              <h4 className="text-2xl font-bold text-darkGreen mt-1">{analytics.average_anxiety || 0} <span className="text-xs font-normal text-gray-400">/ 10</span></h4>
              <p className="text-[11px] text-gray-500 mt-1">Average anxiety level this week</p>
            </div>
          </div>

          <div className="bg-white border border-borderGreen/50 rounded-2xl p-5 flex items-start gap-4">
            <div className="p-3 bg-orange-50 text-orange-500 rounded-xl">
              <Battery size={20} />
            </div>
            <div>
              <p className="text-xs text-gray-400 font-semibold uppercase">Energy Level</p>
              <h4 className="text-2xl font-bold text-darkGreen mt-1">{analytics.average_energy || 0} <span className="text-xs font-normal text-gray-400">/ 10</span></h4>
              <p className="text-[11px] text-gray-500 mt-1">Average energy rating this week</p>
            </div>
          </div>

          <div className="bg-white border border-borderGreen/50 rounded-2xl p-5 flex items-start gap-4">
            <div className="p-3 bg-purple-50 text-purple-500 rounded-xl">
              <Brain size={20} />
            </div>
            <div>
              <p className="text-xs text-gray-400 font-semibold uppercase">Sleep Quality</p>
              <h4 className="text-2xl font-bold text-darkGreen mt-1">{analytics.average_sleep || 0} <span className="text-xs font-normal text-gray-400">hrs</span></h4>
              <p className="text-[11px] text-gray-500 mt-1">Average hours slept per night</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions Row */}
      <div className="space-y-4">
        <h3 className="text-lg font-serif font-bold text-darkGreen">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div 
                key={idx}
                onClick={item.action}
                className="bg-white border border-borderGreen/50 rounded-2xl p-5 hover:shadow-md cursor-pointer hover:border-primaryGreen/50 transition-all flex flex-col justify-between group"
              >
                <div>
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center border mb-4 ${item.color}`}>
                    <Icon size={20} />
                  </div>
                  <h4 className="font-semibold text-gray-800 group-hover:text-primaryGreen transition-colors">{item.title}</h4>
                  <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">{item.desc}</p>
                </div>
                <div className="mt-4 flex items-center text-xs font-medium text-primaryGreen gap-1 group-hover:translate-x-1 transition-transform">
                  Open tool <ChevronRight size={12} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Ongoing Plans and Streaks Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Streak card */}
        <div className="bg-gradient-to-br from-primaryGreen to-darkGreen rounded-3xl p-6 text-white flex flex-col justify-between shadow-md">
          <div>
            <span className="bg-white/20 border border-white/20 text-white text-xs font-semibold px-3 py-1 rounded-full">
              🌿 Streak Active
            </span>
            <h4 className="text-xl font-medium mt-6">Wellness Mindset</h4>
            <p className="text-xs text-white/80 mt-1">You are consistently reflecting on your thoughts and breathing.</p>
          </div>
          <div className="flex items-end justify-between mt-8">
            <div>
              <span className="text-5xl font-serif font-bold">5</span>
              <span className="text-xs text-white/80 ml-1">days in a row</span>
            </div>
            <div className="p-3 bg-white/20 rounded-2xl">
              <Flame size={28} className="fill-current text-orange-400" />
            </div>
          </div>
        </div>

        {/* Current Wellness Plans */}
        <div className="md:col-span-2 bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-serif font-bold text-darkGreen mb-4">Current Wellness Plans</h3>
            {activePlans.length > 0 ? (
              <div className="space-y-4">
                {activePlans.map(plan => (
                  <div key={plan.id} className="border border-borderGreen/40 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs bg-lightGreen text-primaryGreen font-semibold px-2 py-0.5 rounded">
                          {plan.type}
                        </span>
                        <h4 className="text-sm font-semibold text-gray-800">{plan.title}</h4>
                      </div>
                      <div className="w-full bg-lightGreen rounded-full h-2 mt-3 overflow-hidden">
                        <div 
                          className="bg-primaryGreen h-2 rounded-full transition-all duration-500" 
                          style={{ width: `${plan.progress}%` }}
                        />
                      </div>
                    </div>
                    <div className="flex items-center justify-between gap-4">
                      <div className="text-right">
                        <span className="text-sm font-bold text-primaryGreen">{Math.round(plan.progress)}%</span>
                        <span className="text-xs text-gray-400 block">Progress</span>
                      </div>
                      <button
                        onClick={() => setActivePage('planner')}
                        className="p-2 border border-borderGreen/50 rounded-xl text-gray-500 hover:text-primaryGreen hover:bg-lightGreen/50 transition-colors"
                      >
                        <ChevronRight size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <BookOpen size={36} className="text-gray-300 mx-auto mb-2" />
                <p className="text-xs text-gray-500 italic">No active plans. Generate one to get started!</p>
              </div>
            )}
          </div>
          {activePlans.length > 0 && (
            <button
              onClick={() => setActivePage('planner')}
              className="text-xs font-semibold text-primaryGreen hover:text-darkGreen transition-colors flex items-center justify-center gap-1 mt-4"
            >
              Manage all plans <ChevronRight size={12} />
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}
