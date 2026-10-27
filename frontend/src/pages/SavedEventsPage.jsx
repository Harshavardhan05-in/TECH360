import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bookmark, Calendar, MapPin, Trash2, ArrowRight, Clock, ShieldCheck } from 'lucide-react';
import { authService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import EventCard from '../components/events/EventCard';

export default function SavedEventsPage() {
  const { isAuthenticated } = useAuth();
  const [savedItems, setSavedItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadSaved = () => {
    setLoading(true);
    authService.getSavedEvents()
      .then((res) => setSavedItems(res.data || []))
      .catch((err) => console.error("Error loading saved events", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadSaved();
    }
  }, [isAuthenticated]);

  const handleBookmarkChanged = (eventId, isSaved) => {
    if (!isSaved) {
      setSavedItems(prev => prev.filter(item => item.event_id !== eventId));
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-surface-200 text-text-muted flex items-center justify-center mx-auto border border-border-subtle">
          <Bookmark className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-text-primary tracking-tight">Sign In to View Saved Opportunities</h2>
        <p className="text-xs text-text-secondary max-w-sm mx-auto">
          Keep track of approaching hackathons, deadlines, and receive real-time notifications.
        </p>
        <div>
          <Link
            to="/login"
            className="btn-primary text-xs py-2 px-5 inline-block"
          >
            Sign In to Continue
          </Link>
        </div>
      </div>
    );
  }

  const events = savedItems.map(item => item.event).filter(Boolean);

  return (
    <div className="max-w-[1280px] mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-border-subtle">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-text-primary tracking-tight">
            Saved Opportunities
          </h1>
          <p className="text-xs text-text-secondary">Track deadlines and approaching hackathons.</p>
        </div>
        <span className="text-xs font-mono px-3 py-1 rounded-md bg-surface-200 text-primary border border-border-subtle">
          {savedItems.length} bookmarked
        </span>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {[1, 2].map((i) => (
            <div key={i} className="eh-card p-5 h-48 rounded-xl border border-border-subtle bg-surface-200 animate-pulse" />
          ))}
        </div>
      ) : events.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {events.map((ev, index) => (
            <EventCard 
              key={ev.id} 
              event={{ ...ev, is_saved: true }} 
              cardIndex={index}
              onBookmarkChanged={handleBookmarkChanged}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 px-4 rounded-xl border border-dashed border-border-subtle bg-surface-100 space-y-3">
          <Bookmark className="w-8 h-8 mx-auto text-text-muted" />
          <h3 className="text-sm font-semibold text-text-primary">No saved opportunities yet</h3>
          <p className="text-xs text-text-muted max-w-sm mx-auto">
            Browse hackathons, conferences, and workshops on the homepage or India Explorer and click the bookmark icon to save them here.
          </p>
          <Link to="/" className="btn-primary text-xs inline-block">
            Explore Opportunities
          </Link>
        </div>
      )}
    </div>
  );
}
