import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Download, Loader2, FileText, Database, ShieldCheck 
} from 'lucide-react';
import { authAPI } from '../services/api';

export default function ExportData({ user }) {
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const data = await authAPI.exportData(user.id);
      
      // Create JSON blob
      const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
        JSON.stringify(data, null, 2)
      )}`;
      
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute('href', jsonString);
      downloadAnchor.setAttribute('download', `calmmind_backup_${user.name.toLowerCase().replace(/\s+/g, '_')}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    } catch (err) {
      console.error(err);
      alert('Failed to export user database records. Please try again.');
    } finally {
      setLoading(false);
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
        <h2 className="text-3xl font-serif font-bold text-darkGreen">Export Data</h2>
        <p className="text-gray-500 text-sm">Download a local backup of all your personal wellness records.</p>
      </div>

      <div className="bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs space-y-6">
        <div className="flex items-center gap-3">
          <Database size={24} className="text-primaryGreen" />
          <h3 className="text-base font-serif font-semibold text-darkGreen">Download Data Bundle</h3>
        </div>

        <p className="text-xs text-gray-500 leading-relaxed">
          Your backup bundle will contain all information synced to the local database, including:
        </p>

        {/* Feature List */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-gray-700 font-medium bg-wellnessBg/40 border border-borderGreen/20 p-4 rounded-2xl">
          <div className="flex items-center gap-2">📂 Full Profile Details</div>
          <div className="flex items-center gap-2">💬 Conversations History</div>
          <div className="flex items-center gap-2">📈 All Mood Track Logs</div>
          <div className="flex items-center gap-2">📋 Checklists & Planner goals</div>
          <div className="flex items-center gap-2">⭐ Bookmarked Favorites</div>
          <div className="flex items-center gap-2">🔒 Secure JSON Format</div>
        </div>

        <button
          onClick={handleExport}
          disabled={loading}
          className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-primaryGreen text-white font-medium hover:bg-darkGreen transition-all shadow-md flex items-center justify-center gap-2"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
          Download JSON Backup
        </button>
      </div>

      <div className="bg-white border border-borderGreen/50 rounded-3xl p-6 shadow-xs flex gap-4 items-start">
        <ShieldCheck size={28} className="text-accentGreen mt-0.5 flex-shrink-0" />
        <div>
          <h4 className="text-xs font-semibold text-gray-800 uppercase tracking-wider">Privacy & Ownership</h4>
          <p className="text-xs text-gray-500 leading-relaxed mt-1">
            CalmMind AI stores your mental wellness transcripts locally on your system database. We do not transmit or sell any therapeutic dialogue data to external servers. Your export belongs fully to you.
          </p>
        </div>
      </div>
    </motion.div>
  );
}
