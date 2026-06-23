import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Star, Copy, Trash2, Loader2, Sparkles, BookOpen, AlertCircle
} from 'lucide-react';
import { favoritesAPI } from '../services/api';

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    try {
      setLoading(true);
      const data = await favoritesAPI.getFavorites();
      setFavorites(data);
    } catch (err) {
      console.error('Error fetching favorites:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Remove from favorites?')) {
      try {
        await favoritesAPI.deleteFavorite(id);
        setFavorites(prev => prev.filter(f => f.id !== id));
      } catch (err) {
        console.error('Error deleting favorite:', err);
      }
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="p-6 md:p-8 space-y-8 max-w-4xl mx-auto overflow-y-auto h-full pb-16"
    >
      <div className="border-b border-borderGreen/50 pb-5">
        <h2 className="text-3xl font-serif font-bold text-darkGreen flex items-center gap-2">
          <Star size={28} className="text-primaryGreen fill-current" /> Favorites
        </h2>
        <p className="text-gray-500 text-sm">Access your saved response quotes and exercise summaries.</p>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="animate-spin text-primaryGreen" size={28} />
        </div>
      ) : favorites.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {favorites.map((fav) => (
            <div key={fav.id} className="bg-white border border-borderGreen/50 rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4">
              <div>
                <span className="text-[10px] bg-lightGreen text-primaryGreen font-bold px-2.5 py-0.5 rounded-full uppercase">
                  {fav.type || 'quote'}
                </span>
                <p className="text-xs text-gray-700 leading-relaxed mt-3 whitespace-pre-line italic">
                  "{fav.content}"
                </p>
              </div>

              <div className="flex items-center justify-between border-t border-gray-100 pt-3">
                <span className="text-[10px] text-gray-400">
                  Saved: {fav.saved_at ? fav.saved_at.split(' ')[0] : 'Today'}
                </span>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => handleCopy(fav.content)}
                    className="p-2 text-gray-500 hover:text-primaryGreen hover:bg-lightGreen/40 rounded-xl transition-colors"
                    title="Copy text"
                  >
                    <Copy size={14} />
                  </button>
                  <button
                    onClick={() => handleDelete(fav.id)}
                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition-colors"
                    title="Delete item"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white border border-borderGreen/50 rounded-3xl p-12 text-center text-gray-400 italic">
          <BookOpen size={48} className="mx-auto mb-2 text-gray-300" />
          <p className="text-sm font-medium text-darkGreen">Your bookmarks vault is empty</p>
          <p className="text-xs text-gray-500 max-w-sm mx-auto mt-1 leading-relaxed">
            Click the "Save" action below AI companion responses or prediction logs to catalog them here.
          </p>
        </div>
      )}
    </motion.div>
  );
}
