import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ClipboardList, CheckCircle, Plus, Trash2, Loader2, Sparkles, 
  Brain, Clock, ShieldAlert, Award, Star, ListChecks, CalendarRange
} from 'lucide-react';
import { plansAPI } from '../services/api';

export default function Planner({ user, setRefreshTrigger }) {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);

  // Questionnaire form states
  const [goal, setGoal] = useState('Reduce Stress');
  const [stressLevel, setStressLevel] = useState(5);
  const [sleepQuality, setSleepQuality] = useState(5);
  const [availableTime, setAvailableTime] = useState('15 min');
  const [activities, setActivities] = useState(['Breathing Exercises', 'Journaling']);
  const [challenge, setChallenge] = useState('Overthinking');

  const goalOptions = [
    'Reduce Stress',
    'Improve Sleep',
    'Increase Confidence',
    'Improve Focus',
    'Reduce Anxiety'
  ];

  const timeOptions = [
    '5 min',
    '10 min',
    '15 min',
    '30 min',
    '60 min'
  ];

  const activityOptions = [
    'Breathing Exercises',
    'Meditation',
    'Journaling',
    'Walking',
    'Reading',
    'Fitness',
    'Gratitude Practice'
  ];

  const challengeOptions = [
    'Overthinking',
    'Burnout',
    'Anxiety',
    'Sleep Problems',
    'Lack of Motivation',
    'Low Confidence'
  ];

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      setLoading(true);
      const data = await plansAPI.getPlans();
      setPlans(data);
    } catch (err) {
      console.error('Error fetching plans:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const payload = {
        goal,
        stress_level: parseInt(stressLevel),
        sleep_quality: parseInt(sleepQuality),
        available_time: availableTime,
        activities,
        challenge
      };
      
      const data = await plansAPI.generatePersonalizedPlan(payload);
      if (data.status === 'success') {
        fetchPlans();
        setShowQuestionnaire(false);
        if (setRefreshTrigger) setRefreshTrigger(prev => prev + 1);
      }
    } catch (err) {
      console.error('Error generating personalized plan:', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleCheckboxChange = async (planId, taskIdx, checked) => {
    const targetPlan = plans.find(p => p.id === planId);
    if (!targetPlan) return;

    const updatedTasks = targetPlan.tasks.map((t, idx) => {
      if (idx === taskIdx) {
        return { ...t, done: checked };
      }
      return t;
    });

    setPlans(prev => prev.map(p => {
      if (p.id === planId) {
        const total = updatedTasks.length;
        const done = updatedTasks.filter(t => t.done).length;
        const progress = total > 0 ? (done / total) * 100 : 0;
        return {
          ...p,
          tasks: updatedTasks,
          progress,
          completed: done === total ? 1 : 0
        };
      }
      return p;
    }));

    try {
      await plansAPI.updatePlan(planId, updatedTasks);
      if (setRefreshTrigger) setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      console.error('Error saving plan checkbox:', err);
      fetchPlans();
    }
  };

  const handleDelete = async (planId) => {
    if (window.confirm('Delete this wellness plan?')) {
      try {
        await plansAPI.deletePlan(planId);
        setPlans(prev => prev.filter(p => p.id !== planId));
        if (setRefreshTrigger) setRefreshTrigger(prev => prev + 1);
      } catch (err) {
        console.error('Error deleting plan:', err);
      }
    }
  };

  const toggleActivity = (act) => {
    setActivities(prev => 
      prev.includes(act) ? prev.filter(a => a !== act) : [...prev, act]
    );
  };

  // Helper to parse time-of-day/weekly blocks in tasks
  const parseTaskText = (text) => {
    const prefixes = ["Morning:", "Afternoon:", "Evening:", "Weekly Goal:"];
    for (const prefix of prefixes) {
      if (text.startsWith(prefix)) {
        return {
          type: prefix.replace(':', ''),
          content: text.replace(prefix, '').trim()
        };
      }
    }
    // Fallback based on emoji or keywords
    if (text.includes('☀') || text.toLowerCase().includes('morning')) return { type: 'Morning', content: text };
    if (text.includes('🚶') || text.toLowerCase().includes('afternoon') || text.toLowerCase().includes('walk')) return { type: 'Afternoon', content: text };
    if (text.includes('📓') || text.toLowerCase().includes('evening') || text.toLowerCase().includes('night')) return { type: 'Evening', content: text };
    if (text.includes('🌱') || text.toLowerCase().includes('weekly')) return { type: 'Weekly Goal', content: text };
    return { type: 'General', content: text };
  };

  const getPrefixStyle = (type) => {
    switch(type) {
      case 'Morning': return 'bg-amber-50 text-amber-700 border-amber-200/50';
      case 'Afternoon': return 'bg-sky-50 text-sky-700 border-sky-200/50';
      case 'Evening': return 'bg-indigo-50 text-indigo-700 border-indigo-200/50';
      case 'Weekly Goal': return 'bg-emerald-50 text-emerald-700 border-emerald-200/50';
      default: return 'bg-gray-50 text-gray-700 border-gray-200/50';
    }
  };

  const getPrefixIcon = (type) => {
    switch(type) {
      case 'Morning': return '☀';
      case 'Afternoon': return '🚶';
      case 'Evening': return '📓';
      case 'Weekly Goal': return '🌱';
      default: return '✨';
    }
  };

  const activePlans = plans.filter(p => p.completed === 0);
  const completedPlans = plans.filter(p => p.completed === 1);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="p-6 md:p-8 space-y-8 max-w-6xl mx-auto overflow-y-auto h-full pb-16"
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-borderGreen/50 pb-5">
        <div>
          <h2 className="text-3xl font-serif font-bold text-darkGreen">Wellness Planner</h2>
          <p className="text-gray-500 text-sm">Create smart, AI-tailored wellness checklists powered by your goals and mood history.</p>
        </div>
        {!showQuestionnaire && (
          <button
            onClick={() => setShowQuestionnaire(true)}
            className="px-5 py-3 rounded-xl bg-primaryGreen text-white font-medium hover:bg-darkGreen hover:shadow-md transition-all flex items-center gap-2 self-start md:self-auto"
          >
            <Sparkles size={16} /> New AI Plan
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Questionnaire overlay or side pane */}
        {showQuestionnaire ? (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="lg:col-span-12 bg-white border border-borderGreen/60 rounded-3xl p-6 md:p-8 shadow-md space-y-6"
          >
            <div className="flex justify-between items-center border-b border-gray-100 pb-4">
              <h3 className="text-xl font-serif font-semibold text-darkGreen flex items-center gap-2">
                <Sparkles className="text-primaryGreen" size={20} /> AI Personalized Plan Questionnaire
              </h3>
              <button 
                onClick={() => setShowQuestionnaire(false)}
                className="text-gray-400 hover:text-gray-600 text-sm font-medium px-3 py-1 rounded-lg hover:bg-gray-100 transition-all"
              >
                Cancel
              </button>
            </div>

            <form onSubmit={handleGenerate} className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Goal */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
                  <Star size={14} className="text-primaryGreen" /> 1. Wellness Goal
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {goalOptions.map(opt => (
                    <button
                      type="button" key={opt}
                      onClick={() => setGoal(opt)}
                      className={`p-3 text-xs rounded-xl text-left border font-medium transition-all ${
                        goal === opt
                          ? 'bg-lightGreen border-primaryGreen text-primaryGreen font-bold'
                          : 'bg-white border-borderGreen/30 hover:bg-lightGreen/10 text-gray-700'
                      }`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>

              {/* Challenge */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
                  <Brain size={14} className="text-primaryGreen" /> 2. Primary Challenge
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {challengeOptions.map(opt => (
                    <button
                      type="button" key={opt}
                      onClick={() => setChallenge(opt)}
                      className={`p-3 text-xs rounded-xl text-left border font-medium transition-all ${
                        challenge === opt
                          ? 'bg-lightGreen border-primaryGreen text-primaryGreen font-bold'
                          : 'bg-white border-borderGreen/30 hover:bg-lightGreen/10 text-gray-700'
                      }`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>

              {/* Stress Level slider */}
              <div className="bg-wellnessBg/50 border border-borderGreen/20 p-4 rounded-2xl space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
                    <ShieldAlert size={14} className="text-red-500" /> 3. Current Stress Level
                  </label>
                  <span className="text-red-600 font-bold text-sm bg-red-50 px-2.5 py-0.5 rounded-full border border-red-100">{stressLevel} / 10</span>
                </div>
                <input
                  type="range" min="1" max="10" value={stressLevel}
                  onChange={(e) => setStressLevel(e.target.value)}
                  className="w-full h-1.5 bg-lightGreen rounded-lg appearance-none cursor-pointer accent-primaryGreen"
                />
                <div className="flex justify-between text-[10px] text-gray-400">
                  <span>Relaxed (1)</span>
                  <span>Extremely Stressed (10)</span>
                </div>
              </div>

              {/* Sleep Quality slider */}
              <div className="bg-wellnessBg/50 border border-borderGreen/20 p-4 rounded-2xl space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
                    <CalendarRange size={14} className="text-blue-500" /> 4. Current Sleep Quality
                  </label>
                  <span className="text-blue-600 font-bold text-sm bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-100">{sleepQuality} / 10</span>
                </div>
                <input
                  type="range" min="1" max="10" value={sleepQuality}
                  onChange={(e) => setSleepQuality(e.target.value)}
                  className="w-full h-1.5 bg-lightGreen rounded-lg appearance-none cursor-pointer accent-primaryGreen"
                />
                <div className="flex justify-between text-[10px] text-gray-400">
                  <span>Poor Rest (1)</span>
                  <span>Restful Sleep (10)</span>
                </div>
              </div>

              {/* Available Time */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
                  <Clock size={14} className="text-primaryGreen" /> 5. Daily Available Time
                </label>
                <div className="flex flex-wrap gap-2">
                  {timeOptions.map(opt => (
                    <button
                      type="button" key={opt}
                      onClick={() => setAvailableTime(opt)}
                      className={`px-4 py-2 text-xs rounded-xl border font-medium transition-all ${
                        availableTime === opt
                          ? 'bg-lightGreen border-primaryGreen text-primaryGreen font-bold'
                          : 'bg-white border-borderGreen/30 hover:bg-lightGreen/10 text-gray-700'
                      }`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>

              {/* Activities Checklist */}
              <div className="space-y-2 md:col-span-2">
                <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
                  <ListChecks size={14} className="text-primaryGreen" /> 6. Preferred Activities
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {activityOptions.map(act => {
                    const isSelected = activities.includes(act);
                    return (
                      <button
                        type="button" key={act}
                        onClick={() => toggleActivity(act)}
                        className={`p-3 text-xs rounded-xl text-left border font-medium transition-all ${
                          isSelected
                            ? 'bg-lightGreen border-primaryGreen text-primaryGreen font-bold'
                            : 'bg-white border-borderGreen/30 hover:bg-lightGreen/10 text-gray-700'
                        }`}
                      >
                        <input
                          type="checkbox" readOnly checked={isSelected}
                          className="mr-2 rounded border-gray-300 text-primaryGreen focus:ring-primaryGreen"
                        />
                        {act}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="md:col-span-2 pt-4 border-t border-gray-100 flex justify-end gap-3">
                <button
                  type="button" onClick={() => setShowQuestionnaire(false)}
                  className="px-6 py-3 rounded-xl border border-gray-200 text-sm font-medium hover:bg-gray-50 transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit" disabled={generating}
                  className="px-8 py-3 rounded-xl bg-primaryGreen text-white font-medium hover:bg-darkGreen transition-all shadow-md flex items-center gap-2"
                >
                  {generating ? (
                    <>
                      <Loader2 size={16} className="animate-spin" /> Generating Plan...
                    </>
                  ) : (
                    <>
                      <Sparkles size={16} /> Generate AI Plan
                    </>
                  )}
                </button>
              </div>
            </form>
          </motion.div>
        ) : null}

        {/* Current checklists */}
        <div className={showQuestionnaire ? "lg:col-span-12 space-y-6 mt-4" : "lg:col-span-12 space-y-6"}>
          {/* Active Plans checklist */}
          <div className="space-y-4">
            <h3 className="text-lg font-serif font-bold text-darkGreen flex items-center gap-2">
              <ClipboardList size={18} className="text-primaryGreen" /> Current Wellness Plans
            </h3>
            
            {loading ? (
              <div className="flex justify-center py-12 bg-white rounded-3xl border border-borderGreen/30">
                <Loader2 className="animate-spin text-primaryGreen" size={28} />
              </div>
            ) : activePlans.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {activePlans.map(plan => (
                  <div key={plan.id} className="bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs flex flex-col justify-between space-y-4 hover:shadow-sm transition-all">
                    <div>
                      <div className="flex items-start justify-between gap-4 border-b border-gray-50 pb-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] bg-lightGreen text-primaryGreen font-bold px-2 py-0.5 rounded">
                              {plan.type}
                            </span>
                            <span className="text-[10px] text-gray-400">
                              Started: {plan.created_at.split(' ')[0]}
                            </span>
                          </div>
                          <h4 className="text-lg font-serif font-semibold text-darkGreen mt-1">{plan.title}</h4>
                          <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{plan.description}</p>
                        </div>
                        <button
                          onClick={() => handleDelete(plan.id)}
                          className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition-colors shrink-0"
                          title="Delete plan"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>

                      {/* Task list with specific styling */}
                      <div className="space-y-3 mt-4">
                        {plan.tasks && plan.tasks.map((task, idx) => {
                          const parsed = parseTaskText(task.task);
                          return (
                            <label 
                              key={idx}
                              className="flex items-start gap-3 p-3 rounded-2xl bg-wellnessBg/40 border border-borderGreen/15 hover:border-borderGreen/40 cursor-pointer select-none transition-all"
                            >
                              <input
                                type="checkbox"
                                checked={task.done}
                                onChange={(e) => handleCheckboxChange(plan.id, idx, e.target.checked)}
                                className="mt-1 rounded border-gray-300 text-primaryGreen focus:ring-primaryGreen"
                              />
                              <div className="flex-1">
                                <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-md border mr-2 uppercase tracking-wide ${getPrefixStyle(parsed.type)}`}>
                                  <span>{getPrefixIcon(parsed.type)}</span>
                                  <span>{parsed.type}</span>
                                </span>
                                <span className={`text-xs leading-relaxed font-medium ${task.done ? 'line-through text-gray-400' : 'text-gray-700'}`}>
                                  {parsed.content}
                                </span>
                              </div>
                            </label>
                          );
                        })}
                      </div>
                    </div>

                    {/* Progress Meter */}
                    <div className="flex items-center justify-between gap-4 border-t border-gray-50 pt-4 mt-2">
                      <div className="flex-1">
                        <div className="w-full bg-lightGreen h-2 rounded-full overflow-hidden">
                          <div 
                            className="bg-primaryGreen h-2 rounded-full transition-all duration-300"
                            style={{ width: `${plan.progress}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-xs font-bold text-primaryGreen whitespace-nowrap">{Math.round(plan.progress)}% completed</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white border border-borderGreen/50 rounded-3xl p-12 text-center text-gray-400 italic">
                <ClipboardList size={40} className="mx-auto mb-3 text-gray-300" />
                <p className="text-xs">No active wellness plans.</p>
                <button
                  onClick={() => setShowQuestionnaire(true)}
                  className="mt-4 px-4 py-2.5 bg-lightGreen hover:bg-lightGreen/80 border border-primaryGreen/30 text-primaryGreen rounded-xl text-xs font-semibold transition-all inline-flex items-center gap-1.5"
                >
                  <Sparkles size={14} /> Create Your First AI Plan
                </button>
              </div>
            )}
          </div>

          {/* Completed / Archived plans */}
          {completedPlans.length > 0 && (
            <div className="space-y-4 pt-4 border-t border-gray-100">
              <h3 className="text-sm font-bold uppercase tracking-wider text-accentGreen flex items-center gap-2">
                <Award size={16} className="text-primaryGreen" /> Completed Plans
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {completedPlans.map(plan => (
                  <div key={plan.id} className="bg-white border border-borderGreen/40 rounded-2xl p-4 flex items-center justify-between shadow-xs opacity-75">
                    <div className="flex items-center gap-3">
                      <CheckCircle size={18} className="text-primaryGreen shrink-0" />
                      <div>
                        <h4 className="text-xs font-semibold text-gray-700 line-through truncate max-w-[150px]">{plan.title}</h4>
                        <span className="text-[9px] text-gray-400 block">Completed: {plan.created_at.split(' ')[0]}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDelete(plan.id)}
                      className="p-1.5 text-gray-400 hover:text-red-500 rounded-lg hover:bg-red-50 transition-colors"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

