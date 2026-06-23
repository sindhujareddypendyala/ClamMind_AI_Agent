import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, Mic, Volume2, VolumeX, Sparkles, AlertCircle, Loader2, Copy, Bookmark, BookmarkCheck
} from 'lucide-react';
import { chatAPI, voiceAPI, favoritesAPI } from '../services/api';
import VoiceModal from './VoiceModal';

export default function ChatArea({ 
  user, 
  currentConversationId, 
  setCurrentConversationId, 
  setRefreshTrigger,
  setActivePage
}) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [isVoiceOpen, setIsVoiceOpen] = useState(false);
  const [ttsLoadingId, setTtsLoadingId] = useState(null);
  const [playingMessageId, setPlayingMessageId] = useState(null);
  const [favorites, setFavorites] = useState([]);
  const [latestRecommendation, setLatestRecommendation] = useState(null);
  
  const audioRef = useRef(null);
  const bottomRef = useRef(null);

  // Load message logs
  useEffect(() => {
    setLatestRecommendation(null);
    if (currentConversationId) {
      fetchMessages();
    } else {
      setMessages([]);
    }
  }, [currentConversationId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  // Load Favorites to show saved icon
  useEffect(() => {
    if (user) {
      fetchFavorites();
    }
  }, [user]);

  const fetchMessages = async () => {
    try {
      setLoading(true);
      const data = await chatAPI.getMessages(currentConversationId);
      setMessages(data);
    } catch (err) {
      console.error('Error fetching messages:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchFavorites = async () => {
    try {
      const data = await favoritesAPI.getFavorites();
      setFavorites(data);
    } catch (err) {
      console.error('Error fetching favorites:', err);
    }
  };

  const handleStartChat = async () => {
    try {
      setLoading(true);
      const data = await chatAPI.createConversation();
      if (data.status === 'success') {
        setCurrentConversationId(data.conversation.id);
        setRefreshTrigger(prev => prev + 1);
      }
    } catch (err) {
      console.error('Error starting chat:', err);
    } finally {
      setLoading(false);
    }
  };

  const streamResponseText = (fullText) => {
    return new Promise((resolve) => {
      let currentText = '';
      const words = fullText.split(' ');
      let wordIndex = 0;
      const tempId = `streaming_${Date.now()}`;
      
      setMessages(prev => [...prev, { id: tempId, role: 'assistant', content: '' }]);

      const interval = setInterval(() => {
        if (wordIndex < words.length) {
          currentText += (wordIndex === 0 ? '' : ' ') + words[wordIndex];
          setMessages(prev => prev.map(m => m.id === tempId ? { ...m, content: currentText } : m));
          wordIndex++;
        } else {
          clearInterval(interval);
          resolve();
        }
      }, 40);
    });
  };

  const handleSend = async (textToSend = inputText) => {
    const text = textToSend.trim();
    if (!text || sending) return;

    setInputText('');
    setSending(true);
    setLatestRecommendation(null);

    // Optimistically add user message
    const userMsg = { id: Date.now(), role: 'user', content: text, created_at: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);

    try {
      const data = await chatAPI.sendMessage(currentConversationId, text);
      if (data.status === 'success') {
        const fullResponseText = data.response.content;
        
        // Save recommendations metadata to state
        setLatestRecommendation({
          emotion: data.response.emotion,
          exercises: data.response.exercises,
          plan: data.response.plan
        });

        // Stop the thinking indicator
        setSending(false);
        
        // Progressively stream text onto screen
        await streamResponseText(fullResponseText);
        
        // Fetch full message list to get proper ids and timestamps
        const updated = await chatAPI.getMessages(currentConversationId);
        setMessages(updated);
        setRefreshTrigger(prev => prev + 1);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setSending(false);
      // Append system warning
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'system',
        content: 'Failed to deliver message. Please check connection and try again.'
      }]);
    }
  };

  const handleTranscription = (transcript) => {
    if (transcript && transcript.trim()) {
      setInputText(transcript);
    }
  };

  const handleCopyText = (content) => {
    navigator.clipboard.writeText(content);
    alert('Copied to clipboard!');
  };

  const toggleFavorite = async (message) => {
    const isFav = favorites.find(f => f.content === message.content);
    try {
      if (isFav) {
        await favoritesAPI.deleteFavorite(isFav.id);
      } else {
        await favoritesAPI.addFavorite('response', message.content);
      }
      fetchFavorites();
    } catch (err) {
      console.error('Error toggling favorite:', err);
    }
  };

  const handleTTS = async (message) => {
    if (playingMessageId === message.id) {
      // Pause current audio
      if (audioRef.current) {
        audioRef.current.pause();
        setPlayingMessageId(null);
      }
      return;
    }

    try {
      setTtsLoadingId(message.id);
      const audioBlob = await voiceAPI.textToSpeech(message.content);
      const audioUrl = URL.createObjectURL(audioBlob);
      
      if (audioRef.current) {
        audioRef.current.pause();
      }
      
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      
      audio.onended = () => {
        setPlayingMessageId(null);
      };
      
      setPlayingMessageId(message.id);
      audio.play();
    } catch (err) {
      console.error('TTS Error:', err);
    } finally {
      setTtsLoadingId(null);
    }
  };

  const isFavorite = (content) => {
    return favorites.some(f => f.content === content);
  };

  const renderRecommendationButtons = () => {
    if (!latestRecommendation) return null;
    const { emotion, exercises, plan } = latestRecommendation;
    const buttons = [];

    // Stress recovery
    if (emotion === 'stress' || emotion === 'stressed' || emotion === 'overwhelmed') {
      buttons.push({
        label: '🌬 Start Breathing Exercise',
        action: () => {
          sessionStorage.setItem('auto_start_breathing', 'true');
          setActivePage('exercises');
        }
      });
    }

    // Anxiety recovery
    if (emotion === 'anxiety' || emotion === 'anxious') {
      buttons.push({
        label: '🌬 Start Calm Breathing',
        action: () => {
          sessionStorage.setItem('auto_start_breathing', 'true');
          setActivePage('exercises');
        }
      });
      buttons.push({
        label: '🧘 Start Grounding Exercise',
        action: () => {
          sessionStorage.setItem('active_exercise_tab', 'bodyscan');
          setActivePage('exercises');
        }
      });
    }

    // Sadness recovery
    if (emotion === 'sadness' || emotion === 'sad' || emotion === 'lonely') {
      buttons.push({
        label: '🧘 Start Gratitude Exercise',
        action: () => {
          setActivePage('favorites');
        }
      });
    }

    // Burnout recovery
    if (emotion === 'burnout' || emotion === 'overwhelmed') {
      buttons.push({
        label: '📋 Open Recovery Plan',
        action: () => {
          setActivePage('planner');
        }
      });
    }

    // Always allow Open Wellness Plan if a plan is recommended
    if (plan && !buttons.some(b => b.label.includes('Plan'))) {
      buttons.push({
        label: `📋 Open ${plan}`,
        action: () => {
          setActivePage('planner');
        }
      });
    }

    // Always allow wellness exercise if recommended
    if (exercises && exercises.wellness && !buttons.some(b => b.label.includes('🧘'))) {
      buttons.push({
        label: `🧘 Start ${exercises.wellness}`,
        action: () => {
          sessionStorage.setItem('active_exercise_tab', 'pmr');
          setActivePage('exercises');
        }
      });
    }

    // Continue conversation button
    buttons.push({
      label: '💚 Continue Conversation',
      action: () => {
        setInputText("I'm ready to keep talking.");
        setLatestRecommendation(null);
      }
    });

    return buttons.map((btn, idx) => (
      <button
        key={idx}
        onClick={btn.action}
        className="px-4 py-2 text-xs font-semibold rounded-xl bg-white border border-borderGreen/50 text-darkGreen hover:bg-primaryGreen hover:text-white hover:border-primaryGreen transition-all shadow-xs flex items-center gap-1.5"
      >
        {btn.label}
      </button>
    ));
  };

  // -------------------------------------------------------------
  // LANDING PAGE HERO VIEW
  // -------------------------------------------------------------
  if (!currentConversationId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 md:p-12 bg-wellnessBg overflow-y-auto h-full select-none">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-12 gap-12 items-center"
        >
          {/* Left Hero Content */}
          <div className="lg:col-span-7 space-y-6 text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-lightGreen border border-borderGreen/50 text-primaryGreen text-xs font-semibold">
              🧠 CalmMind AI
            </div>
            <h1 className="text-4xl md:text-5xl font-serif text-darkGreen font-extrabold leading-tight">
              Your Personal Mental Wellness Companion
            </h1>
            <p className="text-gray-600 text-sm md:text-base leading-relaxed">
              CalmMind AI helps users manage stress, anxiety, overthinking, emotional wellness, motivation, and daily wellbeing through AI-powered conversations and personalized wellness recommendations.
            </p>
            
            {/* Features Bullet List */}
            <div className="grid grid-cols-2 gap-3 text-sm text-gray-700 font-medium">
              <div className="flex items-center gap-2">🟢 Manage Stress</div>
              <div className="flex items-center gap-2">🟢 Relieve Anxiety</div>
              <div className="flex items-center gap-2">🟢 Stop Overthinking</div>
              <div className="flex items-center gap-2">🟢 Emotional Guidance</div>
              <div className="flex items-center gap-2">🟢 High Motivation</div>
              <div className="flex items-center gap-2">🟢 Daily Wellbeing</div>
            </div>

            <div className="pt-4">
              <button
                onClick={handleStartChat}
                className="inline-flex items-center justify-center gap-2.5 px-8 py-4 rounded-2xl bg-primaryGreen text-white text-base font-semibold hover:bg-darkGreen transition-all shadow-lg hover:shadow-xl hover:translate-y-[-1px]"
              >
                🚀 Start Chat
              </button>
            </div>
          </div>

          {/* Right Hero Illustration */}
          <div className="lg:col-span-5 flex justify-center">
            <motion.div 
              animate={{ y: [0, -10, 0] }}
              transition={{ repeat: Infinity, duration: 5, ease: "easeInOut" }}
              className="relative w-72 h-72 md:w-80 md:h-80 rounded-3xl bg-white border border-borderGreen/60 p-6 flex flex-col items-center justify-center text-center shadow-xl overflow-hidden"
            >
              {/* Inner Circle mandala */}
              <div className="absolute inset-0 bg-gradient-to-tr from-lightGreen/50 to-white -z-10" />
              
              <svg className="w-48 h-48 text-primaryGreen/20 absolute opacity-50" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" stroke="currentColor" strokeWidth="1" fill="none" />
                <circle cx="50" cy="50" r="30" stroke="currentColor" strokeWidth="1.5" fill="none" />
                <circle cx="50" cy="50" r="20" stroke="currentColor" strokeWidth="2" fill="none" />
                <path d="M 50 0 L 50 100 M 0 50 L 100 50" stroke="currentColor" strokeWidth="0.5" />
              </svg>

              <span className="text-6xl mb-4 z-10">🌿</span>
              <h3 className="text-xl font-serif text-darkGreen font-bold z-10">Mindful Awareness</h3>
              <p className="text-xs text-gray-500 max-w-[200px] mt-2 leading-relaxed z-10">
                A calm workspace designed to help you breathe, record your moods, and think therapeutically.
              </p>
            </motion.div>
          </div>
        </motion.div>
      </div>
    );
  }

  // -------------------------------------------------------------
  // ACTIVE CHAT SCREEN VIEW
  // -------------------------------------------------------------
  return (
    <div className="flex-1 flex flex-col h-full bg-white relative">
      {/* Chat header */}
      <div className="px-6 py-4 border-b border-borderGreen/40 flex items-center justify-between bg-wellnessBg/60 backdrop-blur-md">
        <div>
          <h2 className="text-sm font-bold text-darkGreen uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles size={14} className="text-primaryGreen" /> AI Wellness Companion
          </h2>
          <p className="text-xs text-gray-400">Therapeutic synthesis active</p>
        </div>
      </div>

      {/* Messages viewport */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {loading ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-400 gap-2">
            <Loader2 className="animate-spin text-primaryGreen" size={28} />
            <p className="text-xs">Loading dialogue history...</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-400 text-center select-none px-4">
            <span className="text-4xl mb-3">🌿</span>
            <h4 className="text-base font-serif text-darkGreen font-semibold">Start your companion session</h4>
            <p className="text-xs text-gray-500 max-w-sm mt-1">
              Say hello or express how you feel. We'll run the multi-agent checks to support you.
            </p>
          </div>
        ) : (
          <div className="space-y-6 max-w-3xl mx-auto">
            {messages.map((msg) => {
              const isUser = msg.role === 'user';
              const isSys = msg.role === 'system';
              
              if (isSys) {
                return (
                  <div key={msg.id} className="flex justify-center">
                    <div className="flex items-center gap-2 bg-red-50 border border-red-100 text-red-700 px-4 py-2.5 rounded-2xl text-xs">
                      <AlertCircle size={14} />
                      {msg.content}
                    </div>
                  </div>
                );
              }

              return (
                <div key={msg.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                  <div className={`flex gap-3 max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                    {/* Avatar placeholder */}
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold ${
                      isUser ? 'bg-primaryGreen text-white' : 'bg-lightGreen text-primaryGreen border border-borderGreen'
                    }`}>
                      {isUser ? 'ME' : 'AI'}
                    </div>
                    
                    {/* Bubble */}
                    <div className="space-y-1">
                      <div className={`px-4 py-3 rounded-2xl shadow-xs text-sm leading-relaxed ${
                        isUser 
                          ? 'bg-primaryGreen text-white rounded-tr-none' 
                          : 'bg-wellnessBg text-gray-800 border border-borderGreen/50 rounded-tl-none'
                      }`}>
                        {msg.content}
                      </div>
                      
                      {/* Sub-actions for assistant */}
                      {!isUser && (
                        <div className="flex items-center gap-3 px-1 text-gray-400 text-xs">
                          <button
                            onClick={() => handleTTS(msg)}
                            className="hover:text-primaryGreen flex items-center gap-0.5"
                            title="Listen to response"
                          >
                            {ttsLoadingId === msg.id ? (
                              <Loader2 size={12} className="animate-spin" />
                            ) : playingMessageId === msg.id ? (
                              <VolumeX size={12} className="text-red-500" />
                            ) : (
                              <Volume2 size={12} />
                            )}
                            <span className="text-[10px]">Speech</span>
                          </button>
                          
                          <button
                            onClick={() => toggleFavorite(msg)}
                            className="hover:text-primaryGreen flex items-center gap-0.5"
                            title="Add to Favorites"
                          >
                            {isFavorite(msg.content) ? (
                              <BookmarkCheck size={12} className="text-primaryGreen" />
                            ) : (
                              <Bookmark size={12} />
                            )}
                            <span className="text-[10px]">Save</span>
                          </button>

                          <button
                            onClick={() => handleCopyText(msg.content)}
                            className="hover:text-primaryGreen text-[10px]"
                          >
                            Copy
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Local optimistic generation state */}
        {sending && (
          <div className="space-y-6 max-w-3xl mx-auto">
            <div className="flex justify-start">
              <div className="flex gap-3 max-w-[85%] flex-row">
                <div className="w-8 h-8 rounded-full bg-lightGreen text-primaryGreen border border-borderGreen flex items-center justify-center text-xs font-semibold">
                  AI
                </div>
                <div className="px-4 py-3 rounded-2xl bg-wellnessBg text-gray-800 border border-borderGreen/50 rounded-tl-none flex items-center gap-2">
                  <span className="text-xs text-accentGreen font-semibold animate-pulse">🌿 CalmMind is thinking</span>
                  <div className="flex gap-1 items-center">
                    <span className="w-1 h-1 bg-accentGreen rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-1 h-1 bg-accentGreen rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-1 h-1 bg-accentGreen rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {latestRecommendation && !sending && (
          <div className="max-w-3xl mx-auto mt-4 p-5 rounded-2xl bg-lightGreen/30 border border-borderGreen/40 space-y-3">
            <p className="text-xs font-bold text-accentGreen uppercase tracking-wider flex items-center gap-1.5 select-none">
              <Sparkles size={12} className="text-primaryGreen" /> CalmMind Recommended Support
            </p>
            <div className="flex flex-wrap gap-2">
              {renderRecommendationButtons()}
            </div>
          </div>
        )}
        
        <div ref={bottomRef} />
      </div>

      {/* ChatGPT-style input bar */}
      <div className="p-4 border-t border-borderGreen/40 bg-white sticky bottom-0">
        {messages.length === 0 && (
          <div className="max-w-3xl mx-auto flex flex-wrap gap-2 mb-3 justify-center">
            {[
              { text: "😰 I'm Stressed", msg: "I am feeling stressed and need support." },
              { text: "🤯 I'm Overthinking", msg: "I am overthinking and want to calm my thoughts." },
              { text: "😴 Help Me Sleep", msg: "I am having trouble sleeping and need help to relax." },
              { text: "💪 Motivate Me", msg: "I am feeling unmotivated and need a boost." },
              { text: "❤️ Emotional Support", msg: "I need some emotional support and validation." }
            ].map((btn, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSend(btn.msg)}
                className="px-4 py-2 rounded-full border border-borderGreen/60 bg-wellnessBg text-xs font-semibold text-darkGreen hover:bg-lightGreen/50 hover:border-primaryGreen/50 transition-all shadow-xs"
              >
                {btn.text}
              </button>
            ))}
          </div>
        )}
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          className="max-w-3xl mx-auto flex items-center gap-3"
        >
          {/* Rounded Input Container */}
          <div className="relative flex-1 flex items-center bg-wellnessBg border border-borderGreen/60 rounded-2xl px-4 py-2 hover:border-primaryGreen/40 transition-colors shadow-xs">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="How are you feeling today?"
              className="flex-1 bg-transparent text-sm text-gray-800 focus:outline-none pr-10"
              disabled={sending}
            />
            {/* Microphone Icon inside input bar */}
            <button
              type="button"
              onClick={() => setIsVoiceOpen(true)}
              className="absolute right-3 text-gray-400 hover:text-primaryGreen transition-colors p-1 rounded-full hover:bg-lightGreen/50"
              title="Record Voice"
            >
              <Mic size={18} />
            </button>
          </div>

          {/* Green Send Button */}
          <button
            type="submit"
            disabled={sending || !inputText.trim()}
            className={`p-3 rounded-2xl text-white shadow-md transition-all flex items-center justify-center ${
              !inputText.trim() || sending
                ? 'bg-gray-300 cursor-not-allowed shadow-none'
                : 'bg-primaryGreen hover:bg-darkGreen hover:shadow-lg'
            }`}
          >
            <Send size={18} />
          </button>
        </form>
      </div>

      {/* Voice Recorder Overlay Modal */}
      <VoiceModal 
        isOpen={isVoiceOpen} 
        onClose={() => setIsVoiceOpen(false)} 
        onTranscriptionComplete={handleTranscription} 
      />
    </div>
  );
}
