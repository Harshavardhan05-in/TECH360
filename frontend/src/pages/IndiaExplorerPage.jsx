import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  MapPin, ShieldCheck, AlertTriangle, Globe, 
  Search, ArrowRight, ArrowLeft, RefreshCw, 
  ChevronRight, Sparkles, Building2
} from 'lucide-react';
import { regionService, eventService } from '../services/api';
import EventCard from '../components/events/EventCard';

// Deterministic hash to assign one of 5 distinct solid complementary backgrounds
const getStateVariant = (slug) => {
  if (!slug) return 0;
  let hash = 0;
  for (let i = 0; i < slug.length; i++) {
    hash = ((hash << 5) - hash) + slug.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash) % 5;
};

const VARIANT_PILL_STYLES = [
  'bg-primary/10 text-primary border-primary/25',
  'bg-green/10 text-green border-green/25',
  'bg-gold/15 text-gold border-gold/30',
  'bg-rose/15 text-rose border-rose/30',
  'bg-surface-300 text-text-secondary border-border-strong',
];

export default function IndiaExplorerPage() {
  const { stateSlug } = useParams();
  const [regions, setRegions] = useState([]);
  const [currentRegion, setCurrentRegion] = useState(null);
  const [verifiedEvents, setVerifiedEvents] = useState([]);
  const [unverifiedEvents, setUnverifiedEvents] = useState([]);
  const [activeTab, setActiveTab] = useState('verified'); // verified or unverified
  const [includeOnline, setIncludeOnline] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  // Load all regions for state browsing
  useEffect(() => {
    if (!stateSlug) {
      setLoading(true);
      regionService.getRegions()
        .then((res) => {
          const sorted = [...(res.data || [])].sort((a, b) => a.name.localeCompare(b.name));
          setRegions(sorted);
        })
        .catch((err) => console.error("Error loading regions", err))
        .finally(() => setLoading(false));
    }
  }, [stateSlug]);

  // Load specific state data and strictly filtered events
  useEffect(() => {
    if (stateSlug) {
      setLoading(true);
      Promise.all([
        regionService.getRegionDetail(stateSlug),
        // Verified events strictly belonging to this state
        eventService.getEvents({
          state_slug: stateSlug,
          verification_status: 'verified',
          include_online: includeOnline
        }),
        // Unverified events queue
        eventService.getEvents({
          state_slug: stateSlug,
          verification_status: 'unverified',
          include_online: false
        })
      ])
        .then(([regRes, verifiedRes, unverifiedRes]) => {
          setCurrentRegion(regRes.data);
          setVerifiedEvents(verifiedRes.data.items || []);
          setUnverifiedEvents(unverifiedRes.data.items || []);
        })
        .catch((err) => console.error("Error loading state data", err))
        .finally(() => setLoading(false));
    }
  }, [stateSlug, includeOnline]);

  // ══════════════════════════════════════════════════════════
  // VIEW: SINGLE STATE / UT DETAIL LISTING
  // ══════════════════════════════════════════════════════════
  if (stateSlug) {
    return (
      <div className="max-w-[1280px] mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
        {/* Breadcrumb Navigation */}
        <nav aria-label="Breadcrumb" className="flex items-center space-x-2 text-xs text-text-muted">
          <Link to="/" className="hover:text-text-primary transition-colors">Discover</Link>
          <ChevronRight className="w-3.5 h-3.5" />
          <Link to="/india" className="hover:text-text-primary transition-colors">India Explorer</Link>
          <ChevronRight className="w-3.5 h-3.5" />
          <span className="text-text-secondary">{currentRegion?.name || stateSlug.replace('-', ' ')}</span>
        </nav>

        {/* State Banner */}
        <div 
          className="rounded-2xl border border-border-strong bg-surface-200 p-6 sm:p-8 relative overflow-hidden space-y-4 shadow-sm"
        >
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="space-y-2">
              <Link
                to="/india"
                className="inline-flex items-center gap-1.5 text-xs text-primary hover:underline font-semibold"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>All 28 States & 8 Union Territories</span>
              </Link>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl sm:text-3xl font-extrabold text-text-primary tracking-tight">
                  {currentRegion?.name || stateSlug.replace('-', ' ')}
                </h1>
                <span className="font-mono text-xs px-2.5 py-1 rounded-md badge-format font-bold">
                  {currentRegion?.code || 'IN'}
                </span>
              </div>
              <p className="text-xs sm:text-sm text-text-secondary max-w-xl">
                Physical hackathons and developer opportunities strictly occurring within <strong>{currentRegion?.name}</strong>.
              </p>
            </div>

            {/* Toggle Online Events */}
            <div className="flex items-center gap-2 bg-surface-200 p-2.5 rounded-xl border border-border-subtle text-xs">
              <label className="flex items-center gap-2 cursor-pointer select-none text-text-secondary hover:text-text-primary">
                <input
                  type="checkbox"
                  checked={includeOnline}
                  onChange={(e) => setIncludeOnline(e.target.checked)}
                  className="rounded cursor-pointer accent-[#A88AFF]"
                />
                <span>Include Virtual / Online Events</span>
              </label>
            </div>
          </div>

          {/* Verification Tab Pill Switcher */}
          <div className="flex items-center gap-2 pt-2 border-t border-border-subtle">
            <button
              onClick={() => setActiveTab('verified')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                activeTab === 'verified'
                  ? 'btn-primary'
                  : 'text-text-secondary hover:text-text-primary bg-surface-200 border border-border-subtle'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Verified Listings ({verifiedEvents.length})</span>
            </button>

            <button
              onClick={() => setActiveTab('unverified')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                activeTab === 'unverified'
                  ? 'bg-amber text-surface-200 font-bold'
                  : 'text-text-secondary hover:text-text-primary bg-surface-200 border border-border-subtle'
              }`}
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Under Review ({unverifiedEvents.length})</span>
            </button>
          </div>
        </div>

        {/* Events Grid (Desktop: 2 cards per row) */}
        {loading ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {[1, 2].map(i => (
              <div key={i} className="eh-card p-5 h-48 animate-pulse space-y-3">
                <div className="h-4 w-24 bg-surface-300 rounded" />
                <div className="h-6 w-3/4 bg-surface-300 rounded" />
              </div>
            ))}
          </div>
        ) : activeTab === 'verified' ? (
          verifiedEvents.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              {verifiedEvents.map((ev, index) => (
                <EventCard key={ev.id} event={ev} cardIndex={index} />
              ))}
            </div>
          ) : (
            <div className="text-center py-16 px-4 rounded-2xl border border-dashed border-border-subtle bg-surface-100 space-y-2">
              <MapPin className="w-8 h-8 mx-auto text-text-muted" />
              <p className="font-semibold text-text-primary text-sm">No verified physical events currently scheduled in {currentRegion?.name}.</p>
              <p className="text-xs text-text-muted">You can toggle online events above or inspect neighbouring state listings.</p>
            </div>
          )
        ) : (
          unverifiedEvents.length > 0 ? (
            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-gold/10 border border-gold/30 text-xs text-gold flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>These candidate events were discovered by our crawler but await independent venue or circular confirmation.</span>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                {unverifiedEvents.map((ev, index) => (
                  <EventCard key={ev.id} event={ev} cardIndex={index + 2} />
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-14 px-4 rounded-2xl border border-dashed border-border-subtle bg-surface-100 text-xs text-text-muted">
              Unverified candidates queue is clear for {currentRegion?.name}.
            </div>
          )
        )}
      </div>
    );
  }

  // ══════════════════════════════════════════════════════════
  // VIEW: MAIN INDIA EXPLORER GRID (28 States + 8 UTs)
  // ══════════════════════════════════════════════════════════
  const filteredRegions = regions.filter(r => 
    r.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    r.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-[1280px] mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-8">
      {/* Header */}
      <div className="eh-card p-6 sm:p-8 space-y-4 relative overflow-hidden">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md badge-verified text-xs font-mono font-medium">
          <MapPin className="w-3.5 h-3.5" />
          <span>All 28 States & 8 Union Territories</span>
        </div>
        <h1 className="text-2xl sm:text-4xl font-extrabold text-text-primary tracking-tight">
          India Tech Explorer
        </h1>
        <p className="text-xs sm:text-sm text-text-secondary max-w-2xl leading-relaxed">
          Discover hackathons, engineering summits, and developer meetups across all <strong>28 Indian states</strong> and <strong>8 union territories</strong>.
        </p>

        {/* Search State / UT Input */}
        <div className="relative max-w-md pt-2">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search state (e.g. Telangana, Karnataka, Delhi, Maharashtra)..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl text-xs sm:text-sm bg-surface-100 border border-border-subtle text-text-primary placeholder:text-text-muted outline-none focus:border-primary transition-colors"
          />
        </div>
      </div>

      {/* Colourful State Tiles Grid (Distinct Solid Backgrounds) */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(12)].map((_, i) => (
            <div key={i} className="h-28 rounded-xl border border-border-subtle bg-surface-200 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredRegions.map((reg) => {
            const isUT = reg.type === 'union_territory';
            const variant = getStateVariant(reg.slug);
            const pillStyle = VARIANT_PILL_STYLES[variant];

            return (
              <Link
                key={reg.id}
                to={`/india/${reg.slug}`}
                className={`state-card-base state-card-variant-${variant} group transition-all duration-200`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2.5">
                    <span 
                      className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${pillStyle}`}
                    >
                      {reg.code ? reg.code.replace('IN-', '') : 'IN'}
                    </span>
                    <span className="text-[10px] font-mono text-text-muted uppercase">
                      {isUT ? 'Union Territory' : 'State'}
                    </span>
                  </div>

                  <h3 className="font-bold text-sm text-text-primary group-hover:text-primary transition-colors leading-snug break-words">
                    {reg.name}
                  </h3>
                </div>

                <div className="pt-3 border-t border-border-subtle mt-3 flex items-center justify-between text-xs">
                  <span className="font-mono text-[11px] text-text-secondary">
                    {reg.event_count > 0 ? (
                      <strong className="text-text-primary font-semibold">{reg.event_count} {reg.event_count === 1 ? 'event' : 'events'}</strong>
                    ) : (
                      '0 scheduled'
                    )}
                  </span>
                  <span className="text-primary group-hover:translate-x-1 transition-transform flex items-center gap-1 font-semibold text-xs">
                    <span>Explore</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
