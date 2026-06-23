import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Smile, Activity, Moon, BookOpen, AlertCircle, Plus, Calendar, Loader2,
  TrendingUp, TrendingDown, ArrowRight, HelpCircle, MessageSquare, Award, Compass, Heart
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { moodAPI } from '../services/api';

export default function MoodTracker({ user, setActivePage }) {
  const [logs, setLogs] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [trendTab, setTrendTab] = useState('daily'); // 'daily', 'weekly', 'monthly', 'manual'

  // Form states
  const [mood, setMood] = useState('Calm');
  const [stress, setStress] = useState(5);
  const [anxiety, setAnxiety] = useState(5);
  const [energy, setEnergy] = useState(6);
  const [sleep, setSleep] = useState(7);
  const [trigger, setTrigger] = useState('');
  const [notes, setNotes] = useState('');
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await moodAPI.getMoodLogs(30);
      setLogs(data.logs || []);
      setAnalytics(data.analytics || null);
    } catch (err) {
      console.error('Error fetching logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);

    const payload = {
      mood,
      stress_level: parseInt(stress),
      anxiety_level: parseInt(anxiety),
      energy_level: parseInt(energy),
      sleep_hours: parseFloat(sleep),
      trigger: trigger.trim(),
      notes: notes.trim()
    };

    try {
      const data = await moodAPI.logMood(payload);
      if (data.status === 'success') {
        setMessage({ type: 'success', text: 'Today\'s check-in saved! 🌿' });
        setTrigger('');
        setNotes('');
        fetchLogs();
      }
    } catch (err) {
      console.error('Error logging mood:', err);
      setMessage({ type: 'error', text: 'Failed to record check-in.' });
    } finally {
      setSubmitting(false);
    }
  };

  const getChartData = () => {
    return logs.map(log => {
      let dateLabel = '';
      try {
        const clean = log.created_at.split(' ')[0];
        const dateObj = new Date(clean);
        dateLabel = dateObj.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
      } catch {
        dateLabel = log.created_at;
      }
      
      return {
        date: dateLabel,
        Stress: log.stress_level,
        Anxiety: log.anxiety_level,
        Energy: log.energy_level,
        Sleep: log.sleep_hours
      };
    });
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'Improving': return <TrendingUp className="text-emerald-500 animate-pulse" size={20} />;
      case 'Declining': return <TrendingDown className="text-red-500 animate-pulse" size={20} />;
      default: return <span className="text-gray-500 text-lg font-bold">➡</span>;
    }
  };

  const getTrendStyle = (trend) => {
    switch (trend) {
      case 'Improving': return 'bg-emerald-50 text-emerald-700 border-emerald-150';
      case 'Declining': return 'bg-red-50 text-red-700 border-red-150';
      default: return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  const handleRecommendationClick = (rec) => {
    if (!setActivePage) return;
    if (rec.type === 'breathing' || rec.type === 'meditation' || rec.type === 'sleep') {
      setActivePage('exercises');
    } else if (rec.type === 'plan' || rec.type === 'journaling') {
      setActivePage('planner');
    }
  };

  const moodsList = [
    { label: '😀 Happy', val: 'Happy' },
    { label: '🌿 Calm', val: 'Calm' },
    { label: '😰 Anxious', val: 'Anxious' },
    { label: '🤯 Stressed', val: 'Stressed' },
    { label: '😔 Sad', val: 'Sad' },
    { label: '😡 Angry', val: 'Angry' },
    { label: '😐 Neutral', val: 'Neutral' }
  ];

  // Set up data for donut chart
  const emotionColors = {
    positive: '#10B981', // emerald
    neutral: '#6B7280',  // gray
    stress: '#EF4444',   // red
    anxiety: '#3B82F6',  // blue
    sadness: '#8B5CF6',  // purple
    burnout: '#F59E0B'   // amber
  };

  const rawDistribution = analytics?.emotion_distribution || {
    stress: 0, anxiety: 0, sadness: 0, positive: 0, neutral: 0, burnout: 0
  };

  const emotionData = [
    { name: 'Positive', value: rawDistribution.positive || 0, color: emotionColors.positive },
    { name: 'Neutral', value: rawDistribution.neutral || 0, color: emotionColors.neutral },
    { name: 'Stress', value: rawDistribution.stress || 0, color: emotionColors.stress },
    { name: 'Anxiety', value: rawDistribution.anxiety || 0, color: emotionColors.anxiety },
    { name: 'Sadness', value: rawDistribution.sadness || 0, color: emotionColors.sadness },
    { name: 'Burnout', value: rawDistribution.burnout || 0, color: emotionColors.burnout }
  ].filter(item => item.value > 0);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto overflow-y-auto h-full pb-16"
    >
      <div className="border-b border-borderGreen/50 pb-5">
        <h2 className="text-3xl font-serif font-bold text-darkGreen">Mood Analytics</h2>
        <p className="text-gray-500 text-sm">Visualize conversation emotions, wellness score trends, and personalized care insights.</p>
      </div>

      {/* Top dashboard metrics row */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          {/* Wellness score card */}
          <div className="md:col-span-4 bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs flex flex-col justify-between items-center text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-tr from-lightGreen/15 to-transparent -z-10" />
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest block mb-1">Overall Wellness Score</span>
            
            <div className="my-3 relative flex items-center justify-center">
              <div className="w-32 h-32 rounded-full border-4 border-lightGreen flex flex-col items-center justify-center bg-wellnessBg/50 shadow-inner">
                <span className="text-4xl font-serif font-bold text-darkGreen">{analytics.wellness_score}</span>
                <span className="text-[10px] text-gray-500 font-semibold">Scale 1-100</span>
              </div>
            </div>

            <div className={`mt-2 flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-semibold ${getTrendStyle(analytics.wellness_trend)}`}>
              {getTrendIcon(analytics.wellness_trend)}
              <span>Trend: {analytics.wellness_trend}</span>
            </div>
          </div>

          {/* Insights list */}
          <div className="md:col-span-5 bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs flex flex-col justify-between">
            <div>
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <MessageSquare size={14} className="text-primaryGreen" /> Chat-Based Insights
              </h4>
              <div className="space-y-3">
                {analytics.insights && analytics.insights.map((insight, idx) => (
                  <div key={idx} className="flex items-start gap-2.5 p-3 rounded-xl bg-wellnessBg/40 border border-borderGreen/15 text-xs text-gray-700 leading-relaxed font-medium">
                    <span className="text-sm shrink-0">💡</span>
                    <p>{insight}</p>
                  </div>
                ))}
                {(!analytics.insights || analytics.insights.length === 0) && (
                  <p className="text-xs text-gray-400 italic">No insights available yet. Keep conversing with CalmMind AI.</p>
                )}
              </div>
            </div>
          </div>

          {/* Personalized recommendations */}
          <div className="md:col-span-3 bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs flex flex-col justify-between">
            <div>
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Compass size={14} className="text-primaryGreen" /> Personalized Recommendations
              </h4>
              <div className="space-y-2.5">
                {analytics.recommendations && analytics.recommendations.map((rec, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleRecommendationClick(rec)}
                    className="w-full p-3.5 rounded-xl border border-borderGreen/40 bg-white hover:bg-lightGreen/15 text-left text-xs font-bold text-primaryGreen transition-all flex items-center justify-between shadow-xs group"
                  >
                    <span className="flex items-center gap-2">
                      <span className="text-base">{rec.icon}</span>
                      <span>{rec.text}</span>
                    </span>
                    <ArrowRight size={14} className="text-gray-400 group-hover:text-primaryGreen group-hover:translate-x-0.5 transition-all" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main sections layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left pane: New manual entry */}
        <div className="lg:col-span-4 bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs">
          <h3 className="text-lg font-serif font-semibold text-darkGreen mb-4 flex items-center gap-2">
            <Plus size={18} className="text-primaryGreen" /> Record Daily Check-In
          </h3>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Mood selector */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Mood Descriptor</label>
              <div className="grid grid-cols-2 gap-2">
                {moodsList.map((m) => (
                  <button
                    key={m.val}
                    type="button"
                    onClick={() => setMood(m.val)}
                    className={`py-2 px-3 text-xs rounded-xl text-left border font-medium transition-all ${
                      mood === m.val
                        ? 'bg-lightGreen border-primaryGreen text-primaryGreen font-bold'
                        : 'bg-white border-borderGreen/30 hover:bg-lightGreen/10 text-gray-700'
                    }`}
                  >
                    {m.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Sliders */}
            <div className="space-y-4">
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-gray-500 uppercase">Stress Level</span>
                  <span className="text-red-500 font-bold">{stress} / 10</span>
                </div>
                <input
                  type="range" min="1" max="10" value={stress}
                  onChange={(e) => setStress(e.target.value)}
                  className="w-full h-1.5 bg-lightGreen rounded-lg appearance-none cursor-pointer accent-primaryGreen"
                />
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-gray-500 uppercase">Anxiety Level</span>
                  <span className="text-blue-500 font-bold">{anxiety} / 10</span>
                </div>
                <input
                  type="range" min="1" max="10" value={anxiety}
                  onChange={(e) => setAnxiety(e.target.value)}
                  className="w-full h-1.5 bg-lightGreen rounded-lg appearance-none cursor-pointer accent-primaryGreen"
                />
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-gray-500 uppercase">Energy Level</span>
                  <span className="text-orange-500 font-bold">{energy} / 10</span>
                </div>
                <input
                  type="range" min="1" max="10" value={energy}
                  onChange={(e) => setEnergy(e.target.value)}
                  className="w-full h-1.5 bg-lightGreen rounded-lg appearance-none cursor-pointer accent-primaryGreen"
                />
              </div>
            </div>

            {/* Sleep Hours */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-500 uppercase">Sleep Hours</label>
              <input
                type="number" min="0" max="24" step="0.5" value={sleep}
                onChange={(e) => setSleep(e.target.value)}
                className="w-full bg-wellnessBg border border-borderGreen/60 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primaryGreen text-gray-800"
              />
            </div>

            {/* Triggers */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-500 uppercase">Trigger(s)</label>
              <input
                type="text" placeholder="e.g. Exam load, work pressure" value={trigger}
                onChange={(e) => setTrigger(e.target.value)}
                className="w-full bg-wellnessBg border border-borderGreen/60 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primaryGreen text-gray-800"
              />
            </div>

            {/* Notes */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-500 uppercase">Notes / Reflections</label>
              <textarea
                placeholder="How has your day been?" rows="3" value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full bg-wellnessBg border border-borderGreen/60 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primaryGreen text-gray-800 resize-none"
              />
            </div>

            {message && (
              <div className={`p-3 rounded-xl text-xs flex items-center gap-2 ${
                message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
              }`}>
                <AlertCircle size={14} />
                {message.text}
              </div>
            )}

            <button
              type="submit" disabled={submitting}
              className="w-full py-3.5 rounded-xl bg-primaryGreen text-white font-medium hover:bg-darkGreen transition-all shadow-md flex items-center justify-center gap-2"
            >
              {submitting ? <Loader2 size={16} className="animate-spin" /> : null}
              Save Entry
            </button>
          </form>
        </div>

        {/* Right pane: Trend Charts and Distribution */}
        <div className="lg:col-span-8 space-y-6">
          {/* Trend Chart Card with Tabs */}
          <div className="bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-50 pb-4 mb-4">
              <h3 className="text-lg font-serif font-semibold text-darkGreen flex items-center gap-2">
                <Activity size={18} className="text-primaryGreen" /> Wellness & Mood Trends
              </h3>
              
              {/* Tabs */}
              <div className="flex flex-wrap gap-1 bg-wellnessBg p-1 rounded-xl border border-borderGreen/30 text-xs">
                <button
                  onClick={() => setTrendTab('daily')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                    trendTab === 'daily' ? 'bg-white text-primaryGreen font-bold shadow-xs' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Daily
                </button>
                <button
                  onClick={() => setTrendTab('weekly')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                    trendTab === 'weekly' ? 'bg-white text-primaryGreen font-bold shadow-xs' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Weekly
                </button>
                <button
                  onClick={() => setTrendTab('monthly')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                    trendTab === 'monthly' ? 'bg-white text-primaryGreen font-bold shadow-xs' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Monthly
                </button>
                <button
                  onClick={() => setTrendTab('manual')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                    trendTab === 'manual' ? 'bg-white text-primaryGreen font-bold shadow-xs' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Manual Metrics
                </button>
              </div>
            </div>

            <div className="h-80 w-full">
              {loading ? (
                <div className="h-full flex items-center justify-center">
                  <Loader2 className="animate-spin text-primaryGreen" size={24} />
                </div>
              ) : logs.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  {trendTab === 'daily' && analytics?.daily_trends ? (
                    <LineChart data={analytics.daily_trends} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                      <XAxis dataKey="date" stroke="#94A3B8" style={{ fontSize: '11px' }} />
                      <YAxis domain={[0, 100]} stroke="#94A3B8" style={{ fontSize: '11px' }} />
                      <Tooltip contentStyle={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid #DDE5D0' }} />
                      <Line type="monotone" dataKey="score" stroke="#2E8B57" strokeWidth={2.5} name="Wellness Score" dot={{ r: 4 }} activeDot={{ r: 6 }} />
                    </LineChart>
                  ) : trendTab === 'weekly' && analytics?.weekly_trends ? (
                    <LineChart data={analytics.weekly_trends} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                      <XAxis dataKey="week" stroke="#94A3B8" style={{ fontSize: '11px' }} />
                      <YAxis domain={[0, 100]} stroke="#94A3B8" style={{ fontSize: '11px' }} />
                      <Tooltip contentStyle={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid #DDE5D0' }} />
                      <Line type="monotone" dataKey="score" stroke="#6B8E23" strokeWidth={2.5} name="Wellness Score" dot={{ r: 4 }} activeDot={{ r: 6 }} />
                    </LineChart>
                  ) : trendTab === 'monthly' && analytics?.monthly_trends ? (
                    <LineChart data={analytics.monthly_trends} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                      <XAxis dataKey="month" stroke="#94A3B8" style={{ fontSize: '11px' }} />
                      <YAxis domain={[0, 100]} stroke="#94A3B8" style={{ fontSize: '11px' }} />
                      <Tooltip contentStyle={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid #DDE5D0' }} />
                      <Line type="monotone" dataKey="score" stroke="#8B5CF6" strokeWidth={2.5} name="Wellness Score" dot={{ r: 4 }} activeDot={{ r: 6 }} />
                    </LineChart>
                  ) : (
                    <LineChart data={getChartData()} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                      <XAxis dataKey="date" stroke="#94A3B8" style={{ fontSize: '11px' }} />
                      <YAxis stroke="#94A3B8" style={{ fontSize: '11px' }} />
                      <Tooltip contentStyle={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid #DDE5D0' }} />
                      <Legend style={{ fontSize: '12px' }} />
                      <Line type="monotone" dataKey="Stress" stroke="#EF4444" strokeWidth={2} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="Anxiety" stroke="#3B82F6" strokeWidth={2} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="Sleep" stroke="#8B5CF6" strokeWidth={2} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="Energy" stroke="#F59E0B" strokeWidth={2} dot={{ r: 3 }} />
                    </LineChart>
                  )}
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-gray-400 gap-2 italic">
                  <Calendar size={32} />
                  <p className="text-xs">No logs entered yet. Log your first check-in to activate trends!</p>
                </div>
              )}
            </div>
          </div>

          {/* Emotion Distribution Donut Chart and Pills Card */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs">
              <h3 className="text-base font-serif font-semibold text-darkGreen mb-4 flex items-center gap-1.5">
                <Heart size={16} className="text-red-500 animate-pulse" /> Emotion Distribution
              </h3>
              
              <div className="h-56 w-full relative flex items-center justify-center">
                {emotionData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={emotionData}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={75}
                        paddingAngle={3}
                        dataKey="value"
                      >
                        {emotionData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => `${value}%`} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-xs text-gray-400 italic text-center">No logs recorded.</p>
                )}
                
                {/* Donut Center Label */}
                {emotionData.length > 0 && (
                  <div className="absolute flex flex-col items-center justify-center">
                    <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Top Emotion</span>
                    <span className="text-sm font-serif font-bold text-darkGreen mt-0.5">
                      {emotionData.sort((a,b) => b.value - a.value)[0]?.name}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Distribution Legend List */}
            <div className="bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs flex flex-col justify-center space-y-3">
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Metrics Breakdown</h4>
              <div className="space-y-3">
                {[
                  { name: 'Positive', key: 'positive', color: emotionColors.positive },
                  { name: 'Neutral', key: 'neutral', color: emotionColors.neutral },
                  { name: 'Stress', key: 'stress', color: emotionColors.stress },
                  { name: 'Anxiety', key: 'anxiety', color: emotionColors.anxiety },
                  { name: 'Sadness', key: 'sadness', color: emotionColors.sadness },
                  { name: 'Burnout', key: 'burnout', color: emotionColors.burnout }
                ].map(item => {
                  const pct = rawDistribution[item.key] || 0;
                  return (
                    <div key={item.key} className="space-y-1">
                      <div className="flex justify-between items-center text-xs font-medium text-gray-600">
                        <span className="flex items-center gap-1.5">
                          <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                          <span>{item.name}</span>
                        </span>
                        <span className="font-bold text-gray-800">{pct}%</span>
                      </div>
                      <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full rounded-full transition-all duration-500" style={{ backgroundColor: item.color, width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* History log lists */}
          <div className="bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs max-h-[350px] overflow-y-auto">
            <h3 className="text-lg font-serif font-semibold text-darkGreen mb-4 flex items-center gap-2 sticky top-0 bg-white pb-2 border-b border-gray-100 z-10">
              Check-In History
            </h3>
            <div className="space-y-4">
              {logs.slice().reverse().map((log) => (
                <div key={log.id} className="border-b border-gray-100 pb-4 last:border-b-0 last:pb-0">
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <span className="font-semibold text-darkGreen bg-lightGreen/50 px-2.5 py-0.5 rounded-full">
                      {log.mood}
                    </span>
                    <span className="text-gray-400">
                      {log.created_at.split('.')[0]}
                    </span>
                  </div>
                  {log.trigger && (
                    <p className="text-xs text-gray-600 font-medium">
                      Trigger: <span className="text-gray-500 font-normal">{log.trigger}</span>
                    </p>
                  )}
                  {log.notes && (
                    <p className="text-xs text-gray-500 italic mt-1 bg-wellnessBg/50 p-2 rounded-lg border border-borderGreen/20">
                      "{log.notes}"
                    </p>
                  )}
                  {/* Render parameters only if they are manual logs or filled */}
                  {(log.stress_level > 0 || log.anxiety_level > 0 || log.energy_level > 0 || log.sleep_hours > 0) ? (
                    <div className="flex items-center gap-3 text-[10px] text-gray-400 mt-2">
                      <span>Stress: <strong className="text-red-500">{log.stress_level}</strong></span>
                      <span>Anxiety: <strong className="text-blue-500">{log.anxiety_level}</strong></span>
                      <span>Energy: <strong className="text-orange-500">{log.energy_level}</strong></span>
                      <span>Sleep: <strong className="text-purple-500">{log.sleep_hours}h</strong></span>
                    </div>
                  ) : log.wellness_score > 0 ? (
                    <div className="flex items-center gap-3 text-[10px] text-gray-400 mt-2 font-medium">
                      <span>Wellness Score: <strong className="text-primaryGreen font-bold">{log.wellness_score}</strong></span>
                      <span>Auto-Tracked via Chat Analysis</span>
                    </div>
                  ) : null}
                </div>
              ))}
              {logs.length === 0 && (
                <p className="text-xs text-gray-400 italic text-center py-4">No entries recorded.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
