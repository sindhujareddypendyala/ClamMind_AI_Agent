import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Sparkles, Star, AlertCircle, Calendar, ShieldAlert, Loader2, Award, HeartHandshake
} from 'lucide-react';
import { moodAPI, favoritesAPI } from '../services/api';

export default function Prediction({ user }) {
  const [days, setDays] = useState(7);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    runAnalysis();
  }, [days]);

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);
    setSaved(false);
    
    try {
      const data = await moodAPI.predictMood(days);
      if (data.success) {
        setResult(data);
      } else {
        setError(data.message || 'No prediction available for the selected range.');
        setResult(null);
      }
    } catch (err) {
      console.error(err);
      setError('Could not complete mood analysis. Please make sure you have logged enough mood entries.');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveFavorite = async () => {
    if (!result) return;
    const confidence = extractConfidence(result.analysis);
    const summary = `Prediction Report (${days} days): Stress Avg: ${result.avg_stress}/10. Coping: ${confidence}%. Insight: ${result.analysis.slice(0, 150)}...`;
    
    try {
      await favoritesAPI.addFavorite('exercise', summary);
      setSaved(true);
      alert('Saved insights report to your favorites! ⭐');
    } catch (err) {
      console.error('Error saving prediction summary:', err);
    }
  };

  const extractConfidence = (text) => {
    const match = text.match(/(\d+)\s*%/);
    return match ? parseInt(match[1]) : 65; // Reasonable default
  };

  const getCopingStatus = (score) => {
    if (score < 40) return { label: 'Low Coping Capacity', color: 'text-red-600 bg-red-50 border-red-100', bar: 'bg-red-500' };
    if (score < 70) return { label: 'Moderate Coping Capacity', color: 'text-amber-600 bg-amber-50 border-amber-100', bar: 'bg-amber-500' };
    return { label: 'Excellent Coping Capacity', color: 'text-primaryGreen bg-lightGreen border-borderGreen/40', bar: 'bg-primaryGreen' };
  };

  const confidenceScore = result ? extractConfidence(result.analysis) : 65;
  const coping = getCopingStatus(confidenceScore);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="p-6 md:p-8 space-y-8 max-w-4xl mx-auto overflow-y-auto h-full pb-16"
    >
      <div className="border-b border-borderGreen/50 pb-5">
        <h2 className="text-3xl font-serif font-bold text-darkGreen flex items-center gap-2">
          <Sparkles size={28} className="text-primaryGreen" /> Mood Prediction & Insights
        </h2>
        <p className="text-gray-500 text-sm">AI-driven coping forecasts and wellness analysis based on your logs.</p>
      </div>

      {/* Select timeline */}
      <div className="bg-white border border-borderGreen/50 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
        <div className="flex items-center gap-3">
          <Calendar size={18} className="text-accentGreen" />
          <span className="text-sm font-semibold text-gray-600 uppercase">Analysis Window</span>
          <select
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value))}
            className="bg-wellnessBg border border-borderGreen/60 rounded-xl px-3 py-1.5 text-xs font-semibold text-darkGreen focus:outline-none"
          >
            <option value={7}>Last 7 Days</option>
            <option value={14}>Last 14 Days</option>
            <option value={30}>Last 30 Days</option>
          </select>
        </div>
        <p className="text-xs text-gray-500 max-w-md leading-relaxed">
          The AI analyst processes your stress level, sleep quality, and reported triggers to forecast emotional wellness outcomes.
        </p>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-gray-400 gap-2">
          <Loader2 className="animate-spin text-primaryGreen" size={32} />
          <p className="text-xs">Running model regressions & calculating insights...</p>
        </div>
      ) : error ? (
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 text-center max-w-md mx-auto space-y-4">
          <AlertCircle className="mx-auto text-amber-500" size={36} />
          <h4 className="text-base font-semibold text-amber-800">Needs More Log Data</h4>
          <p className="text-xs text-amber-700 leading-relaxed">
            {error}
          </p>
          <div className="pt-2">
            <span className="text-xs font-semibold text-gray-500 uppercase block mb-1">Tip</span>
            <p className="text-[11px] text-gray-500">Log your stress levels and sleep daily for at least 3-4 days to enable prediction models.</p>
          </div>
        </div>
      ) : result ? (
        <div className="space-y-6">
          {/* Metrics summary cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white border border-borderGreen/50 rounded-2xl p-5 text-center shadow-xs">
              <span className="text-xs text-gray-400 font-semibold uppercase">Logs Evaluated</span>
              <h4 className="text-2xl font-bold text-darkGreen mt-2">{result.logs_count} Entries</h4>
            </div>
            <div className="bg-white border border-borderGreen/50 rounded-2xl p-5 text-center shadow-xs">
              <span className="text-xs text-gray-400 font-semibold uppercase">Average Stress</span>
              <h4 className="text-2xl font-bold text-darkGreen mt-2">{result.avg_stress} / 10</h4>
            </div>
            <div className="bg-white border border-borderGreen/50 rounded-2xl p-5 text-center shadow-xs">
              <span className="text-xs text-gray-400 font-semibold uppercase">Average Sleep</span>
              <h4 className="text-2xl font-bold text-darkGreen mt-2">{result.avg_sleep} hrs</h4>
            </div>
          </div>

          {/* Trend badges */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-white border border-borderGreen/40 text-center shadow-xs">
              <span className="text-[10px] uppercase font-bold text-gray-400">Stress Trend</span>
              <p className="text-sm font-semibold text-gray-700 mt-1">{result.stress_trend}</p>
            </div>
            <div className="p-4 rounded-xl bg-white border border-borderGreen/40 text-center shadow-xs">
              <span className="text-[10px] uppercase font-bold text-gray-400">Anxiety Trend</span>
              <p className="text-sm font-semibold text-gray-700 mt-1">{result.anxiety_trend}</p>
            </div>
          </div>

          {/* Coping capacity gauge meter */}
          <div className="bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-bold uppercase tracking-wider text-accentGreen">Coping Capacity Outlook</h3>
              <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full border ${coping.color}`}>
                {coping.label}
              </span>
            </div>

            {/* Premium Linear Gauge */}
            <div className="space-y-2">
              <div className="w-full bg-lightGreen h-3.5 rounded-full overflow-hidden flex">
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ${coping.bar}`}
                  style={{ width: `${confidenceScore}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-400 font-semibold px-0.5">
                <span>0% (Overwhelmed)</span>
                <span className="text-darkGreen font-bold">{confidenceScore}% Coping Capacity</span>
                <span>100% (Resilient)</span>
              </div>
            </div>
          </div>

          {/* Detailed analysis insights */}
          <div className="bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <h3 className="text-base font-serif font-bold text-darkGreen flex items-center gap-2">
                <Award size={18} className="text-primaryGreen" /> AI Synthesis Report
              </h3>
              
              <button
                onClick={handleSaveFavorite}
                disabled={saved}
                className={`flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-xl border transition-all ${
                  saved 
                    ? 'bg-lightGreen border-borderGreen/40 text-primaryGreen cursor-not-allowed'
                    : 'bg-white border-borderGreen/50 text-gray-600 hover:bg-lightGreen/20'
                }`}
              >
                <Star size={14} className={saved ? 'fill-current' : ''} /> {saved ? 'Saved' : 'Save Summary'}
              </button>
            </div>

            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
              {result.analysis}
            </p>
          </div>
        </div>
      ) : null}
    </motion.div>
  );
}
