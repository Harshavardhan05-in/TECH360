import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Sparkles, Compass, MapPin, Globe, ShieldCheck, 
  ArrowRight, RefreshCw, Flame, ChevronRight, 
  Code, Cpu, Layers, Trophy, Users, Laptop
} from 'lucide-react';
import { eventService } from '../services/api';
import EventCard from '../components/events/EventCard';
import SearchFilters from '../components/search/SearchFilters';
import HeroOpportunityVisual from '../components/home/HeroOpportunityVisual';

const CATEGORY_TILES = [
  { id: 'all', label: 'All Events', icon: Layers, accentClass: 'text-primary', lightClass: 'cat-tile-all' },
  { id: 'hackathon', label: 'Hackathons', icon: Code, accentClass: 'text-[#B95335] dark:text-[#E6B887]', lightClass: 'cat-tile-hackathon' },
  { id: 'workshop', label: 'Workshops', icon: Cpu, accentClass: 'text-[#294C40] dark:text-[#6CA58C]', lightClass: 'cat-tile-workshop' },
  { id: 'conference', label: 'Conferences', icon: Globe, accentClass: 'text-[#D9A441] dark:text-[#E6B887]', lightClass: 'cat-tile-conference' },
  { id: 'competition', label: 'Competitions', icon: Trophy, accentClass: 'text-[#C76B83] dark:text-[#C76B83]', lightClass: 'cat-tile-competition' },
  { id: 'meetup', label: 'Meetups', icon: Users, accentClass: 'text-[#8D536D] dark:text-[#8D536D]', lightClass: 'cat-tile-meetup' },
];

export default function HomePage() {
  const [events, setEvents] = useState([]);
  const [closingSoonEvents, setClosingSoonEvents] = useState([]);
  const [onlineEvents, setOnlineEvents] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [page, setPage] = useState(1);

  const [filters, setFilters] = useState({
    q: '',
    category: 'all',
    format: 'all',
    date_preset: 'all',
    state_slug: undefined,
    is_free: undefined,
    sort_by: 'start_date',
  });

  const fetchEvents = async (pageNum = 1, append = false) => {
    if (append) {
      setLoadingMore(true);
    } else {
      setLoading(true);
    }

    try {
      const params = {
        page: pageNum,
        page_size: 10,
        sort_by: filters.sort_by,
      };
      if (filters.q) params.q = filters.q;
      if (filters.category && filters.category !== 'all') params.category = filters.category;
      if (filters.format && filters.format !== 'all') params.format = filters.format;
      if (filters.date_preset && filters.date_preset !== 'all') params.date_preset = filters.date_preset;
      if (filters.state_slug && filters.state_slug !== 'all') params.state_slug = filters.state_slug;
      if (filters.is_free !== undefined) params.is_free = filters.is_free;

      const res = await eventService.getEvents(params);
      
      if (append) {
        setEvents(prev => [...prev, ...res.data.items]);
      } else {
        setEvents(res.data.items);
      }
      setTotal(res.data.total);

      // On initial load without active search, fetch Closing Soon and Online sections
      if (pageNum === 1 && !filters.q && filters.category === 'all') {
        eventService.getEvents({ page_size: 4, sort_by: 'deadline' })
          .then(closingRes => {
            const now = new Date();
            const validClosing = (closingRes.data.items || []).filter(
              e => e.registration_deadline && new Date(e.registration_deadline) > now
            ).slice(0, 2);
            setClosingSoonEvents(validClosing);
          })
          .catch(() => {});

        eventService.getEvents({ page_size: 2, format: 'online' })
          .then(onlineRes => {
            setOnlineEvents(onlineRes.data.items || []);
          })
          .catch(() => {});
      }
    } catch (err) {
      console.error("Failed to load events", err);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  useEffect(() => {
    setPage(1);
    fetchEvents(1, false);
  }, [filters]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleResetFilters = () => {
    setFilters({
      q: '',
      category: 'all',
      format: 'all',
      date_preset: 'all',
      state_slug: undefined,
      is_free: undefined,
      sort_by: 'start_date',
    });
  };

  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchEvents(nextPage, true);
  };

  const hasMore = events.length < total;

  // Derive two featured events for the featured section
  const featuredEvents = events.slice(0, 2);

  return (
    <div className="max-w-[1280px] mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-10">

      {/* ══════════════════════════════════════════════════════════
          SECTION 1: HERO
          Visual and immersive with headline, short subtitle,
          distinctive visual, and prominent event search.
         ══════════════════════════════════════════════════════════ */}
      <section className="rounded-2xl bg-surface-200 border border-border-strong p-6 sm:p-8 relative overflow-hidden shadow-sm hero-light-surface">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
          
          {/* Left Column: Headline, short subtitle, hotspots */}
          <div className="lg:col-span-8 space-y-4">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold bg-surface-300 text-text-secondary border border-border-subtle hero-light-badge">
              <Sparkles className="w-3.5 h-3.5 text-primary" />
              <span>Verified Developer Events & Hackathons</span>
            </div>

            <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-text-primary leading-tight hero-light-headline">
              Find Your Next Hackathon, Conference & Workshop
            </h1>

            <p className="text-xs sm:text-sm text-text-secondary leading-relaxed max-w-2xl hero-light-subtitle">
              Discover authentic developer competitions, student hackathons, and engineering summits across India and worldwide with verified registration links.
            </p>

            {/* Quick Hub Shortcuts */}
            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
              <span className="text-[11px] font-medium text-text-muted hero-light-label mr-1">Popular Hubs:</span>
              {[
                { to: '/india/telangana', label: 'Telangana (Hyderabad)' },
                { to: '/india/karnataka', label: 'Karnataka (Bengaluru)' },
                { to: '/india/delhi', label: 'Delhi NCR' },
                { to: '/india/maharashtra', label: 'Maharashtra (Mumbai)' },
                { to: '/global', label: 'Global Online' },
              ].map(chip => (
                <Link
                  key={chip.to}
                  to={chip.to}
                  className="px-2.5 py-1 rounded-lg bg-surface-100 border border-border-subtle text-text-secondary hover:text-text-primary hover:border-primary transition-colors text-[11px] font-medium hero-light-chip"
                >
                  {chip.label}
                </Link>
              ))}
            </div>
          </div>

          {/* Right Column: Discovering hackathons & connecting developers visual */}
          <div className="hidden lg:flex lg:col-span-4 justify-center items-center">
            <HeroOpportunityVisual />
          </div>
        </div>

        {/* ══════════════════════════════════════════════════════════
            SECTION 3: FUNCTIONAL EVENT SEARCH & COMPACT FILTERS
           ══════════════════════════════════════════════════════════ */}
        <div className="pt-6 mt-6 border-t border-border-subtle hero-light-divider">
          <SearchFilters
            filters={filters}
            onFilterChange={handleFilterChange}
            onResetFilters={handleResetFilters}
            totalResults={total}
          />
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          SECTION 4: FEATURED EVENTS
          Two large, colourful gradient cards side by side on desktop.
         ══════════════════════════════════════════════════════════ */}
      {featuredEvents.length >= 2 && !filters.q && (filters.category === 'all') && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" />
              <h2 className="text-base sm:text-lg font-bold text-text-primary tracking-tight">
                Featured Flagships
              </h2>
            </div>
            <span className="text-[11px] font-mono text-text-muted">
              Editor's spotlight
            </span>
          </div>

          {/* Two large colourful gradient cards side by side on desktop */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <EventCard 
              event={featuredEvents[0]} 
              featured={true} 
              featuredVariant={1} 
            />
            <EventCard 
              event={featuredEvents[1]} 
              featured={true} 
              featuredVariant={2} 
            />
          </div>
        </section>
      )}

      {/* ══════════════════════════════════════════════════════════
          SECTION 5: EVENT CATEGORIES
          Colourful tiles for Hackathons, Workshops, Conferences, 
          Competitions, Meetups.
         ══════════════════════════════════════════════════════════ */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base sm:text-lg font-bold text-text-primary tracking-tight">
            Browse by Category
          </h2>
          <span className="text-[11px] font-mono text-text-muted">
            Filter by format
          </span>
        </div>

        {/* Colourful Category Tiles with Solid Backgrounds */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
          {CATEGORY_TILES.map((cat) => {
            const Icon = cat.icon;
            const active = (filters.category || 'all') === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => handleFilterChange('category', cat.id)}
                className={`p-3.5 rounded-xl border flex flex-col items-center justify-center gap-2 text-center transition-all cursor-pointer cat-tile-base ${cat.lightClass} ${
                  active 
                    ? 'bg-surface-300 border-primary shadow-sm scale-[1.02] cat-tile-active' 
                    : 'bg-surface-200 border-border-subtle hover:border-border-strong hover:bg-surface-100'
                }`}
              >
                <div 
                  className={`w-9 h-9 rounded-lg flex items-center justify-center transition-transform cat-tile-icon-bg ${
                    active ? 'bg-primary text-background' : 'bg-surface-100 ' + cat.accentClass
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <span className={`text-xs cat-tile-label ${active ? 'font-bold text-text-primary' : 'font-medium text-text-secondary'}`}>
                  {cat.label}
                </span>
              </button>
            );
          })}
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          SECTION 6: UPCOMING EVENTS
          Desktop: two cards per row with solid colourful cards.
         ══════════════════════════════════════════════════════════ */}
      <section className="space-y-8">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h2 className="text-base sm:text-lg font-bold text-text-primary tracking-tight">
                {filters.category && filters.category !== 'all'
                  ? `${filters.category.charAt(0).toUpperCase() + filters.category.slice(1)} Opportunities`
                  : 'Upcoming Verified Events'}
              </h2>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-surface-200 border border-border-subtle text-text-muted">
                {total} found
              </span>
            </div>

            <button
              onClick={() => fetchEvents(1, false)}
              title="Refresh event list"
              className="p-1.5 rounded-lg text-text-muted hover:text-text-primary bg-surface-200 border border-border-subtle transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-primary' : ''}`} />
            </button>
          </div>

          {/* Events Grid (Desktop: 2 cards per row) */}
          {loading && events.length === 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="eh-card p-5 h-52 animate-pulse space-y-3">
                  <div className="h-4 w-24 bg-surface-300 rounded" />
                  <div className="h-6 w-3/4 bg-surface-300 rounded" />
                  <div className="h-4 w-1/2 bg-surface-300 rounded" />
                  <div className="h-10 w-full bg-surface-300 rounded mt-4" />
                </div>
              ))}
            </div>
          ) : events.length > 0 ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                {events.map((ev, index) => (
                  <EventCard key={ev.id} event={ev} cardIndex={index} />
                ))}
              </div>

              {/* Load More Pagination */}
              {hasMore && (
                <div className="flex flex-col items-center justify-center pt-2 space-y-2">
                  <button
                    onClick={handleLoadMore}
                    disabled={loadingMore}
                    className="btn-secondary px-6 py-2.5 text-xs font-semibold flex items-center gap-2 rounded-xl transition-all"
                  >
                    {loadingMore ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin text-primary" />
                        <span>Loading opportunities...</span>
                      </>
                    ) : (
                      <>
                        <span>Load More Events ({total - events.length} remaining)</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </>
                    )}
                  </button>
                  <span className="text-[11px] font-mono text-text-muted">
                    Showing {events.length} of {total} verified events
                  </span>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12 px-4 rounded-xl border border-dashed border-border-subtle bg-surface-200 space-y-3">
              <Compass className="w-8 h-8 mx-auto text-text-muted" />
              <h3 className="text-sm font-semibold text-text-primary">No matching events found</h3>
              <p className="text-xs text-text-muted max-w-sm mx-auto">
                Try widening your search terms or clearing active filters to browse all verified listings.
              </p>
              <button onClick={handleResetFilters} className="btn-primary text-xs">
                Clear All Filters
              </button>
            </div>
          )}
        </div>

        {/* ══════════════════════════════════════════════════════════
            SECTION 7: CLOSING SOON (Clearly Separated Section)
           ══════════════════════════════════════════════════════════ */}
        {closingSoonEvents.length > 0 && !filters.q && filters.category === 'all' && (
          <div className="pt-6 border-t border-border-subtle space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Flame className="w-4 h-4 text-[#B95335] dark:text-[#E6B887]" />
                <h3 className="text-base font-bold text-text-primary tracking-tight">
                  Closing Soon — Final Registration Window
                </h3>
              </div>
              <span className="text-[11px] font-mono text-[#B95335] dark:text-[#E6B887]">
                Urgent deadlines approaching
              </span>
            </div>

            {/* Two cards per row on desktop */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              {closingSoonEvents.map((ev, index) => (
                <EventCard key={`closing-${ev.id}`} event={ev} cardIndex={index + 2} />
              ))}
            </div>
          </div>
        )}

        {/* ══════════════════════════════════════════════════════════
            SECTION 8: ONLINE EVENTS (Clearly Separated Section)
           ══════════════════════════════════════════════════════════ */}
        {onlineEvents.length > 0 && !filters.q && filters.category === 'all' && filters.format !== 'online' && (
          <div className="pt-6 border-t border-border-subtle space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Laptop className="w-4 h-4 text-[#294C40] dark:text-[#6CA58C]" />
                <h3 className="text-base font-bold text-text-primary tracking-tight">
                  Online & Virtual Events
                </h3>
              </div>
              <Link 
                to="/global" 
                className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
              >
                <span>View all virtual</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {/* Two cards per row on desktop */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              {onlineEvents.map((ev, index) => (
                <EventCard key={`online-${ev.id}`} event={ev} cardIndex={index + 1} />
              ))}
            </div>
          </div>
        )}

      </section>

    </div>
  );
}
