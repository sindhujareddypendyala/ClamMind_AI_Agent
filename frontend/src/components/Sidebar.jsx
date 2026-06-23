import React, { useState, useEffect } from 'react';
import { 
  MessageSquare, Calendar, LineChart, Wind, Sparkles, Star, 
  User, Download, LogOut, Plus, Trash2, Edit2, Pin, Check, X, Menu
} from 'lucide-react';
import { chatAPI } from '../services/api';

export default function Sidebar({ 
  user, 
  activePage, 
  setActivePage, 
  currentConversationId, 
  setCurrentConversationId, 
  onLogout,
  refreshTrigger,
  setRefreshTrigger
}) {
  const [conversations, setConversations] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (user) {
      fetchConversations();
    }
  }, [user, refreshTrigger]);

  const fetchConversations = async () => {
    try {
      const data = await chatAPI.getConversations();
      // Ensure data is sorted
      setConversations(data);
    } catch (err) {
      console.error('Error fetching conversations:', err);
    }
  };

  const handleNewChat = async () => {
    try {
      const data = await chatAPI.createConversation();
      if (data.status === 'success') {
        setCurrentConversationId(data.conversation.id);
        setActivePage('chat');
        setRefreshTrigger(prev => prev + 1);
        setMobileOpen(false);
      }
    } catch (err) {
      console.error('Error creating conversation:', err);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (window.confirm('Delete this conversation?')) {
      try {
        await chatAPI.deleteConversation(id);
        if (currentConversationId === id) {
          setCurrentConversationId(null);
        }
        setRefreshTrigger(prev => prev + 1);
      } catch (err) {
        console.error('Error deleting conversation:', err);
      }
    }
  };

  const handlePin = async (id, e) => {
    e.stopPropagation();
    try {
      await chatAPI.pinConversation(id);
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      console.error('Error pinning conversation:', err);
    }
  };

  const startRename = (conv, e) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditTitle(conv.title);
  };

  const saveRename = async (id, e) => {
    e.stopPropagation();
    if (!editTitle.trim()) return;
    try {
      await chatAPI.renameConversation(id, editTitle.trim());
      setEditingId(null);
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      console.error('Error renaming conversation:', err);
    }
  };

  const getGroupedConversations = () => {
    const pinned = conversations.filter(c => c.pinned === 1);
    const unpinned = conversations.filter(c => c.pinned !== 1);

    const groups = {
      Today: [],
      Yesterday: [],
      'Last 7 Days': [],
      Older: [],
    };

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const sevenDaysAgo = new Date(today);
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    unpinned.forEach(conv => {
      const convDate = new Date(conv.created_at.replace(' ', 'T'));
      if (convDate >= today) {
        groups.Today.push(conv);
      } else if (convDate >= yesterday) {
        groups.Yesterday.push(conv);
      } else if (convDate >= sevenDaysAgo) {
        groups['Last 7 Days'].push(conv);
      } else {
        groups.Older.push(conv);
      }
    });

    return { pinned, groups };
  };

  const { pinned, groups } = getGroupedConversations();

  const handleSelectConv = (id) => {
    setCurrentConversationId(id);
    setActivePage('chat');
    setMobileOpen(false);
  };

  const navItems = [
    { id: 'chat', label: 'AI Companion', icon: MessageSquare },
    { id: 'planner', label: 'Wellness Planner', icon: Calendar },
    { id: 'tracker', label: 'Mood Tracker', icon: LineChart },
    { id: 'exercises', label: 'Wellness Exercises', icon: Wind },
    { id: 'prediction', label: 'Mood Prediction', icon: Sparkles },
    { id: 'favorites', label: 'Favorites', icon: Star },
  ];

  const sidebarContent = (
    <div className="flex flex-col h-full bg-wellnessBg border-r border-borderGreen text-gray-800 select-none">
      {/* Brand Header */}
      <div className="p-6 pb-4 border-b border-borderGreen/50">
        <h1 className="text-2xl font-serif font-bold text-primaryGreen flex items-center gap-2">
          <span>🌿</span> CalmMind AI
        </h1>
        <p className="text-xs text-accentGreen mt-1 font-medium">
          Welcome back, {user?.name || 'Friend'} 👋
        </p>
      </div>

      {/* Action Area */}
      <div className="px-4 py-3">
        <button
          onClick={handleNewChat}
          className="flex items-center justify-center gap-2 w-full py-3 rounded-xl bg-primaryGreen text-white font-medium hover:bg-darkGreen transition-all duration-200 shadow-sm"
        >
          <Plus size={18} /> New Chat
        </button>
      </div>

      {/* Navigation List */}
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-6">
        {/* Core Nav */}
        <div className="space-y-1">
          {navItems.map(item => {
            const Icon = item.icon;
            const active = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => { setActivePage(item.id); setMobileOpen(false); }}
                className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  active 
                    ? 'bg-lightGreen text-primaryGreen' 
                    : 'text-gray-600 hover:bg-lightGreen/50 hover:text-darkGreen'
                }`}
              >
                <Icon size={18} className={active ? 'text-primaryGreen' : 'text-gray-400'} />
                {item.label}
              </button>
            );
          })}
        </div>

        {/* History Section */}
        <div>
          <h3 className="px-3 text-xs font-bold uppercase tracking-wider text-accentGreen mb-2">
            History
          </h3>

          {/* Pinned Sub-section */}
          {pinned.length > 0 && (
            <div className="mb-4">
              <p className="px-3 text-[10px] font-semibold text-gray-400 mb-1">📌 Pinned</p>
              <div className="space-y-0.5">
                {pinned.map(conv => renderHistoryItem(conv))}
              </div>
            </div>
          )}

          {/* Chronological Sub-sections */}
          {Object.entries(groups).map(([groupName, items]) => {
            if (items.length === 0) return null;
            return (
              <div key={groupName} className="mb-4">
                <p className="px-3 text-[10px] font-semibold text-gray-400 mb-1">{groupName}</p>
                <div className="space-y-0.5">
                  {items.map(conv => renderHistoryItem(conv))}
                </div>
              </div>
            );
          })}

          {conversations.length === 0 && (
            <p className="px-3 text-xs text-gray-400 italic">No conversations yet.</p>
          )}
        </div>
      </div>

      {/* Settings & Footer Profile */}
      <div className="p-4 border-t border-borderGreen/50 bg-white/40 space-y-1">
        <button
          onClick={() => { setActivePage('profile'); setMobileOpen(false); }}
          className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
            activePage === 'profile' 
              ? 'bg-lightGreen text-primaryGreen' 
              : 'text-gray-600 hover:bg-lightGreen/50'
          }`}
        >
          <User size={18} className="text-gray-400" />
          Edit Profile
        </button>
        <button
          onClick={() => { setActivePage('export'); setMobileOpen(false); }}
          className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
            activePage === 'export' 
              ? 'bg-lightGreen text-primaryGreen' 
              : 'text-gray-600 hover:bg-lightGreen/50'
          }`}
        >
          <Download size={18} className="text-gray-400" />
          Export Data
        </button>
        <button
          onClick={onLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium text-red-600 hover:bg-red-50/50 transition-all"
        >
          <LogOut size={18} className="text-red-500" />
          Logout
        </button>
      </div>
    </div>
  );

  function renderHistoryItem(conv) {
    const isActive = activePage === 'chat' && currentConversationId === conv.id;
    const isEditing = editingId === conv.id;

    return (
      <div
        key={conv.id}
        onClick={() => !isEditing && handleSelectConv(conv.id)}
        className={`group relative flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium cursor-pointer transition-all ${
          isActive 
            ? 'bg-lightGreen text-primaryGreen' 
            : 'text-gray-600 hover:bg-lightGreen/40 hover:text-darkGreen'
        }`}
      >
        {isEditing ? (
          <div className="flex items-center gap-1 w-full mr-8">
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              className="bg-white border border-borderGreen rounded px-1.5 py-0.5 text-xs w-full focus:outline-none focus:border-primaryGreen text-gray-800"
              onClick={(e) => e.stopPropagation()}
            />
            <button 
              onClick={(e) => saveRename(conv.id, e)} 
              className="text-primaryGreen p-0.5 hover:bg-white rounded"
            >
              <Check size={14} />
            </button>
            <button 
              onClick={(e) => { e.stopPropagation(); setEditingId(null); }} 
              className="text-red-500 p-0.5 hover:bg-white rounded"
            >
              <X size={14} />
            </button>
          </div>
        ) : (
          <div className="truncate pr-16 select-none font-normal">
            💬 {conv.title}
          </div>
        )}

        {!isEditing && (
          <div className="absolute right-2 top-1.5 hidden group-hover:flex items-center gap-0.5 bg-fade-gradient p-0.5 rounded">
            <button
              onClick={(e) => handlePin(conv.id, e)}
              className={`p-0.5 rounded hover:bg-lightGreen/80 ${conv.pinned === 1 ? 'text-primaryGreen' : 'text-gray-400'}`}
              title={conv.pinned === 1 ? 'Unpin conversation' : 'Pin conversation'}
            >
              <Pin size={12} className={conv.pinned === 1 ? 'fill-current' : ''} />
            </button>
            <button
              onClick={(e) => startRename(conv, e)}
              className="p-0.5 rounded text-gray-400 hover:text-darkGreen hover:bg-lightGreen/80"
              title="Rename"
            >
              <Edit2 size={12} />
            </button>
            <button
              onClick={(e) => handleDelete(conv.id, e)}
              className="p-0.5 rounded text-gray-400 hover:text-red-500 hover:bg-red-50"
              title="Delete"
            >
              <Trash2 size={12} />
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <>
      {/* Mobile Header */}
      <div className="md:hidden flex items-center justify-between bg-wellnessBg border-b border-borderGreen p-4 w-full sticky top-0 z-40">
        <h1 className="text-xl font-serif font-bold text-primaryGreen flex items-center gap-2">
          <span>🌿</span> CalmMind AI
        </h1>
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-2 rounded-xl border border-borderGreen/50 text-gray-600 bg-white/80"
        >
          <Menu size={20} />
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-40 flex">
          <div className="fixed inset-0 bg-black/30 backdrop-blur-xs" onClick={() => setMobileOpen(false)}></div>
          <div className="relative w-72 h-full z-10 shadow-2xl">
            {sidebarContent}
          </div>
        </div>
      )}

      {/* Desktop Sidebar (Permanent) */}
      <div className="hidden md:block w-72 h-screen flex-shrink-0">
        {sidebarContent}
      </div>
    </>
  );
}
