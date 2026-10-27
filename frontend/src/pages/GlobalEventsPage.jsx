import React, { useState, useEffect } from 'react';
import { Globe, ShieldCheck, RefreshCw, Compass } from 'lucide-react';
import { eventService } from '../services/api';
import EventCard from '../components/events/EventCard';
import SearchFilters from '../components/search/SearchFilters';

export default function GlobalEventsPage() {
  const [events, setEvents] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    q: '',
    category: 'all',
    format: 'all',
    date_preset: 'all',
    is_free: undefined,
    sort_by: 'start_date',
    page: 1,
  });

  const loadGlobalEvents = async () => {
    setLoading(true);
    try {
      const params = {
        page: filters.page,
        page_size: 16,
        sort_by: filters.sort_by,
      };
      if (filters.q) params.q = filters.q;
      if (filters.category && filters.category !== 'all') params.category = filters.category;
      if (filters.format && filters.format !== 'all') params.format = filters.format;
      if (filters.date_preset && filters.date_preset !== 'all') params.date_preset = filters.date_preset;
      if (filters.is_free !== undefined) params.is_free = filters.is_free;

      const res = await eventService.getEvents(params);
      setEvents(res.data.items || []);
      setTotal(res.data.total);
    } catch (err) {
      console.error("Failed to load global events", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGlobalEvents();
  }, [filters]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  };

  const handleResetFilters = () => {
    setFilters({
      q: '',
      category: 'all',
      format: 'all',
      date_preset: 'all',
      is_free: undefined,
      sort_by: 'start_date',
      page: 1,
    });
  };

  return (
    <div className="max-w-[1280px] mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-8">
      {/* Header */}
      <div 
        className="eh-card p-6 sm:p-8 space-y-3 relative overflow-hidden shadow-sm"
      >
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md badge-format text-xs font-mono font-medium">
          <Globe className="w-3.5 h-3.5" />
          <span>Worldwide & Online Virtual Hub</span>
        </div>
        <h1 className="text-2xl sm:text-4xl font-extrabold text-text-primary tracking-tight">
          Global Tech Events & Hackathons
        </h1>
        <p className="text-xs sm:text-sm text-text-secondary max-w-2xl leading-relaxed">
          Discover virtual international buildathons, open-source sprints, and global developer summits accessible from anywhere in the world with verified links.
        </p>
      </div>

      {/* Filters */}
      <SearchFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        onResetFilters={handleResetFilters}
        totalResults={total}
      />

      {/* Grid Header */}
      <div className="flex items-center justify-between pt-2">
        <div className="flex items-center gap-2.5">
          <h2 className="text-base sm:text-lg font-bold text-text-primary tracking-tight">
            Global Listings
          </h2>
          <span className="text-xs font-mono px-2.5 py-0.5 rounded-md bg-surface-100 border border-border-subtle text-text-muted">
            {total} found
          </span>
        </div>
        <button
          onClick={loadGlobalEvents}
          title="Refresh listings"
          className="p-1.5 rounded-lg text-text-muted hover:text-text-primary bg-surface-100 border border-border-subtle transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-primary' : ''}`} />
        </button>
      </div>

      {/* Desktop: 2 Cards Per Row */}
      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="eh-card p-5 h-48 animate-pulse space-y-3">
              <div className="h-4 w-24 bg-surface-300 rounded" />
              <div className="h-6 w-3/4 bg-surface-300 rounded" />
            </div>
          ))}
        </div>
      ) : events.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {events.map((ev, index) => (
            <EventCard key={ev.id} event={ev} cardIndex={index} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 px-4 rounded-xl border border-dashed border-border-subtle bg-surface-100 space-y-3">
          <Compass className="w-8 h-8 mx-auto text-text-muted" />
          <h3 className="text-sm font-semibold text-text-primary">No matching events found</h3>
          <p className="text-xs text-text-muted max-w-sm mx-auto">
            Try resetting your search query or broadening your filters.
          </p>
          <button onClick={handleResetFilters} className="btn-primary text-xs">
            Clear Filters
          </button>
        </div>
      )}
    </div>
  );
}
