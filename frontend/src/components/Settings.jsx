import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  User, ShieldAlert, AlertTriangle, Save, Loader2, Check 
} from 'lucide-react';
import { authAPI } from '../services/api';

export default function Settings({ user, setUser, onLogout }) {
  const [name, setName] = useState(user?.name || '');
  const [age, setAge] = useState(user?.age || 20);
  const [occupation, setOccupation] = useState(user?.occupation || '');
  
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSave = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setMessage({ type: 'error', text: 'Name cannot be empty.' });
      return;
    }

    setSaving(true);
    setMessage(null);

    try {
      const data = await authAPI.saveProfile({
        name: name.trim(),
        age: parseInt(age),
        occupation: occupation.trim()
      });
      
      if (data.status === 'success') {
        setUser(data.user);
        setMessage({ type: 'success', text: 'Profile updated successfully! 🌿' });
      }
    } catch (err) {
      console.error(err);
      setMessage({ type: 'error', text: 'Failed to update profile.' });
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!user) return;
    const confirmText = `Are you absolutely sure you want to delete your profile? All conversations, planner items, favorites, and mood logs will be permanently deleted. This action CANNOT be undone.`;
    
    if (window.confirm(confirmText)) {
      setDeleting(true);
      try {
        await authAPI.deleteProfile(user.id);
        alert('Your profile and all associated data have been permanently deleted.');
        onLogout(); // Clean up app states
      } catch (err) {
        console.error(err);
        alert('Failed to delete profile. Please try again.');
      } finally {
        setDeleting(false);
      }
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="p-6 md:p-8 space-y-8 max-w-2xl mx-auto overflow-y-auto h-full pb-16"
    >
      <div className="border-b border-borderGreen/50 pb-5">
        <h2 className="text-3xl font-serif font-bold text-darkGreen">Edit Profile</h2>
        <p className="text-gray-500 text-sm">Update your personal details to tune therapist synthesis context.</p>
      </div>

      {/* Edit Profile Form */}
      <div className="bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-accentGreen flex items-center gap-2">
          <User size={16} /> Personal Information
        </h3>

        <form onSubmit={handleSave} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-gray-500 uppercase">Full Name</label>
            <input
              type="text" value={name} onChange={(e) => setName(e.target.value)}
              className="w-full bg-wellnessBg border border-borderGreen/60 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primaryGreen text-gray-800"
              placeholder="Full name"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
                className="w-full bg-wellnessBg border border-borderGreen/60 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primaryGreen text-gray-800"
                placeholder="e.g. Student, Engineer"
              />
            </div>
          </div>

          {message && (
            <div className={`p-3 rounded-xl text-xs flex items-center gap-2 ${
              message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            }`}>
              {message.type === 'success' ? <Check size={14} /> : <ShieldAlert size={14} />}
              {message.text}
            </div>
          )}

          <button
            type="submit" disabled={saving}
            className="px-6 py-3 rounded-xl bg-primaryGreen text-white font-medium hover:bg-darkGreen transition-all shadow-md flex items-center justify-center gap-2"
          >
            {saving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
            Save Changes
          </button>
        </form>
      </div>

      {/* Danger Zone */}
      <div className="bg-red-50/30 border border-red-200/50 rounded-3xl p-6 space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-red-600 flex items-center gap-2">
          <AlertTriangle size={16} /> Danger Zone
        </h3>
        <p className="text-xs text-gray-500 leading-relaxed">
          Once you delete your user profile, it cannot be restored. All conversations, favorited items, logs, and wellness planner targets will be instantly wiped out from the local database.
        </p>

        <button
          onClick={handleDeleteAccount}
          disabled={deleting}
          className="px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-semibold text-xs transition-all shadow-xs"
        >
          {deleting ? 'Deleting Profile...' : 'Delete Profile & Data'}
        </button>
      </div>
    </motion.div>
  );
}
