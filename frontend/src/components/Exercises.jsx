import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, Square, Compass, Wind, Sparkles, Volume2, ShieldAlert
} from 'lucide-react';

export default function Exercises() {
  const [activeExercise, setActiveExercise] = useState('breathing'); // 'breathing', 'pmr', 'bodyscan'
  const [breathingActive, setBreathingActive] = useState(false);
  const [phase, setPhase] = useState('inhale'); // 'inhale', 'hold1', 'exhale', 'hold2'
  const [countdown, setCountdown] = useState(4);

  // Auto-trigger exercises from session recommendations
  useEffect(() => {
    const autoStart = sessionStorage.getItem('auto_start_breathing');
    if (autoStart === 'true') {
      setBreathingActive(true);
      sessionStorage.removeItem('auto_start_breathing');
    }

    const activeTab = sessionStorage.getItem('active_exercise_tab');
    if (activeTab) {
      setActiveExercise(activeTab);
      sessionStorage.removeItem('active_exercise_tab');
    }
  }, []);

  // Box Breathing cycle: Inhale 4s -> Hold 4s -> Exhale 4s -> Hold 4s
  useEffect(() => {
    let interval = null;
    if (breathingActive) {
      interval = setInterval(() => {
        setCountdown((prev) => {
          if (prev === 1) {
            // Transition to next phase
            setPhase((currPhase) => {
              if (currPhase === 'inhale') return 'hold1';
              if (currPhase === 'hold1') return 'exhale';
              if (currPhase === 'exhale') return 'hold2';
              return 'inhale';
            });
            return 4; // Reset countdown
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      setCountdown(4);
      setPhase('inhale');
    }
    return () => clearInterval(interval);
  }, [breathingActive]);

  const handleStart = () => {
    setBreathingActive(true);
    setPhase('inhale');
    setCountdown(4);
  };

  const handleStop = () => {
    setBreathingActive(false);
  };

  const getPhaseText = () => {
    if (phase === 'inhale') return '🫁 Breathe In';
    if (phase === 'hold1') return '⏸ Hold';
    if (phase === 'exhale') return '🌬 Breathe Out';
    return '⏸ Hold';
  };

  const getPhaseColor = () => {
    if (phase === 'inhale') return 'bg-emerald-500 text-white';
    if (phase === 'hold1') return 'bg-teal-500 text-white';
    if (phase === 'exhale') return 'bg-sky-500 text-white';
    return 'bg-indigo-500 text-white';
  };

  const getCircleScale = () => {
    if (!breathingActive) return 'scale-100';
    if (phase === 'inhale') return 'scale-130';
    if (phase === 'hold1') return 'scale-130';
    return 'scale-95';
  };

  const getCircleTransition = () => {
    if (!breathingActive) return 'transition-all duration-500';
    if (phase === 'inhale') return 'transition-transform duration-[4000ms] ease-out';
    if (phase === 'exhale') return 'transition-transform duration-[4000ms] ease-in-out';
    return 'transition-transform duration-500'; // quick adjustment during holds
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="p-6 md:p-8 space-y-8 max-w-5xl mx-auto overflow-y-auto h-full pb-16"
    >
      <div className="border-b border-borderGreen/50 pb-5">
        <h2 className="text-3xl font-serif font-bold text-darkGreen">Wellness Exercises</h2>
        <p className="text-gray-500 text-sm">Regulate your autonomic nervous system with guided mindfulness activities.</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-borderGreen/20 gap-4">
        <button
          onClick={() => { handleStop(); setActiveExercise('breathing'); }}
          className={`pb-3 text-sm font-semibold transition-all border-b-2 ${
            activeExercise === 'breathing' 
              ? 'border-primaryGreen text-primaryGreen' 
              : 'border-transparent text-gray-400 hover:text-gray-600'
          }`}
        >
          Box Breathing
        </button>
        <button
          onClick={() => { handleStop(); setActiveExercise('pmr'); }}
          className={`pb-3 text-sm font-semibold transition-all border-b-2 ${
            activeExercise === 'pmr' 
              ? 'border-primaryGreen text-primaryGreen' 
              : 'border-transparent text-gray-400 hover:text-gray-600'
          }`}
        >
          Muscle Relaxation (PMR)
        </button>
        <button
          onClick={() => { handleStop(); setActiveExercise('bodyscan'); }}
          className={`pb-3 text-sm font-semibold transition-all border-b-2 ${
            activeExercise === 'bodyscan' 
              ? 'border-primaryGreen text-primaryGreen' 
              : 'border-transparent text-gray-400 hover:text-gray-600'
          }`}
        >
          Body Scan Meditation
        </button>
      </div>

      {/* Main viewport */}
      <div className="bg-white border border-borderGreen/50 rounded-3xl p-6 md:p-8 shadow-xs min-h-[500px] flex flex-col items-center justify-center">
        
        {/* VIEW 1: BOX BREATHING */}
        {activeExercise === 'breathing' && (
          <div className="flex flex-col items-center justify-center space-y-8 w-full max-w-lg">
            <div className="text-center space-y-2">
              <h3 className="text-xl font-serif text-darkGreen font-bold">Guided Box Breathing</h3>
              <p className="text-xs text-gray-500 leading-relaxed max-w-sm">
                Box Breathing is used by top professionals to restore cognitive clarity and relieve extreme stress in 4 easy blocks.
              </p>
            </div>

            {/* Breathing Circle Container (holds 300px fixed outer box) */}
            <div className="w-80 h-80 flex items-center justify-center relative">
              <div 
                className={`w-60 h-60 rounded-full flex flex-col items-center justify-center text-center shadow-lg border border-white/20 select-none ${getCircleTransition()} ${getCircleScale()} ${
                  breathingActive ? getPhaseColor() : 'bg-lightGreen text-primaryGreen'
                }`}
              >
                <div className="text-2xl font-bold font-serif mb-1">
                  {breathingActive ? getPhaseText() : '🫁 Calm'}
                </div>
                <div className="text-4xl font-extrabold font-serif">
                  {breathingActive ? countdown : 'Ready'}
                </div>
              </div>
            </div>

            {/* Controls */}
            <div className="flex gap-4">
              {!breathingActive ? (
                <button
                  onClick={handleStart}
                  className="flex items-center gap-2 px-6 py-3 rounded-full bg-primaryGreen hover:bg-darkGreen text-white font-semibold transition-all shadow-md"
                >
                  <Play size={16} fill="currentColor" /> Start Breathing
                </button>
              ) : (
                <button
                  onClick={handleStop}
                  className="flex items-center gap-2 px-6 py-3 rounded-full bg-red-500 hover:bg-red-600 text-white font-semibold transition-all shadow-md"
                >
                  <Square size={16} fill="currentColor" /> Stop Exercise
                </button>
              )}
            </div>
          </div>
        )}

        {/* VIEW 2: PROGRESSIVE MUSCLE RELAXATION */}
        {activeExercise === 'pmr' && (
          <div className="w-full max-w-2xl space-y-6 text-left">
            <div className="text-center md:text-left">
              <h3 className="text-2xl font-serif text-darkGreen font-bold mb-2">Progressive Muscle Relaxation (PMR)</h3>
              <p className="text-xs text-gray-500">
                PMR is an somatic therapy technique of tensing and releasing muscle groups to relieve physiological anxiety.
              </p>
            </div>

            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-wellnessBg border border-borderGreen/40 flex items-start gap-4">
                <span className="w-6 h-6 rounded-full bg-primaryGreen text-white font-bold flex items-center justify-center text-xs flex-shrink-0 mt-0.5">1</span>
                <div>
                  <h4 className="text-sm font-semibold text-gray-800">Breath & Prepare</h4>
                  <p className="text-xs text-gray-500 mt-1 leading-relaxed">Sit comfortably, close your eyes, and take three slow abdominal breaths. Allow your shoulders to drop.</p>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-wellnessBg border border-borderGreen/40 flex items-start gap-4">
                <span className="w-6 h-6 rounded-full bg-primaryGreen text-white font-bold flex items-center justify-center text-xs flex-shrink-0 mt-0.5">2</span>
                <div>
                  <h4 className="text-sm font-semibold text-gray-800">Tense Muscle Groups</h4>
                  <p className="text-xs text-gray-500 mt-1 leading-relaxed">Starting with your forehead, squeeze the muscles tight for 5 seconds. Next proceed to your jaw, shoulders, fists, thighs, and feet.</p>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-wellnessBg border border-borderGreen/40 flex items-start gap-4">
                <span className="w-6 h-6 rounded-full bg-primaryGreen text-white font-bold flex items-center justify-center text-xs flex-shrink-0 mt-0.5">3</span>
                <div>
                  <h4 className="text-sm font-semibold text-gray-800">Release & Feel</h4>
                  <p className="text-xs text-gray-500 mt-1 leading-relaxed">Exhale as you release the tension suddenly. Notice the warm, heavy feeling of relaxation flood your muscles for 15 seconds before moving to the next group.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW 3: BODY SCAN MEDITATION */}
        {activeExercise === 'bodyscan' && (
          <div className="w-full max-w-2xl space-y-6 text-left">
            <div className="text-center md:text-left">
              <h3 className="text-2xl font-serif text-darkGreen font-bold mb-2">Body Scan Meditation</h3>
              <p className="text-xs text-gray-500">
                Ground yourself in the present moment by sequentially scanning your body for tension without judgment.
              </p>
            </div>

            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-wellnessBg border border-borderGreen/40 flex items-start gap-4">
                <span className="w-6 h-6 rounded-full bg-primaryGreen text-white font-bold flex items-center justify-center text-xs flex-shrink-0 mt-0.5">1</span>
                <div>
                  <h4 className="text-sm font-semibold text-gray-800">Focus on the Feet</h4>
                  <p className="text-xs text-gray-500 mt-1 leading-relaxed">Lie down or sit upright. Place attention on your toes. Notice if they feel warm, cold, heavy, or tingly. Breathe into them.</p>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-wellnessBg border border-borderGreen/40 flex items-start gap-4">
                <span className="w-6 h-6 rounded-full bg-primaryGreen text-white font-bold flex items-center justify-center text-xs flex-shrink-0 mt-0.5">2</span>
                <div>
                  <h4 className="text-sm font-semibold text-gray-800">Move up the Legs and Torso</h4>
                  <p className="text-xs text-gray-500 mt-1 leading-relaxed">Slowly shift your focus up your calves, knees, thighs, and pelvis. Observe the rise and fall of your belly as you breathe.</p>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-wellnessBg border border-borderGreen/40 flex items-start gap-4">
                <span className="w-6 h-6 rounded-full bg-primaryGreen text-white font-bold flex items-center justify-center text-xs flex-shrink-0 mt-0.5">3</span>
                <div>
                  <h4 className="text-sm font-semibold text-gray-800">Release Neck, Face, and Shoulders</h4>
                  <p className="text-xs text-gray-500 mt-1 leading-relaxed">Settle on your neck and jaw where stress usually gathers. Relax your facial muscles. Let your body rest completely weightless.</p>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </motion.div>
  );
}
