import React, { useState, useEffect } from 'react';
import { 
  Search, X, Globe, MapPin, Calendar, 
  RotateCcw, Tag, Check, Filter
} from 'lucide-react';
import { regionService } from '../../services/api';

const CANONICAL_STATES_FALLBACK = [
  // States
  { slug: "andhra-pradesh", name: "Andhra Pradesh", code: "AP" },
  { slug: "arunachal-pradesh", name: "Arunachal Pradesh", code: "AR" },
  { slug: "assam", name: "Assam", code: "AS" },
  { slug: "bihar", name: "Bihar", code: "BR" },
  { slug: "chhattisgarh", name: "Chhattisgarh", code: "CG" },
  { slug: "goa", name: "Goa", code: "GA" },
  { slug: "gujarat", name: "Gujarat", code: "GJ" },
  { slug: "haryana", name: "Haryana", code: "HR" },
  { slug: "himachal-pradesh", name: "Himachal Pradesh", code: "HP" },
  { slug: "jharkhand", name: "Jharkhand", code: "JH" },
  { slug: "karnataka", name: "Karnataka", code: "KA" },
  { slug: "kerala", name: "Kerala", code: "KL" },
  { slug: "madhya-pradesh", name: "Madhya Pradesh", code: "MP" },
  { slug: "maharashtra", name: "Maharashtra", code: "MH" },
  { slug: "manipur", name: "Manipur", code: "MN" },
  { slug: "meghalaya", name: "Meghalaya", code: "ML" },
  { slug: "mizoram", name: "Mizoram", code: "MZ" },
  { slug: "nagaland", name: "Nagaland", code: "NL" },
  { slug: "odisha", name: "Odisha", code: "OD" },
  { slug: "punjab", name: "Punjab", code: "PB" },
  { slug: "rajasthan", name: "Rajasthan", code: "RJ" },
  { slug: "sikkim", name: "Sikkim", code: "SK" },
  { slug: "tamil-nadu", name: "Tamil Nadu", code: "TN" },
  { slug: "telangana", name: "Telangana", code: "TG" },
  { slug: "tripura", name: "Tripura", code: "TR" },
  { slug: "uttar-pradesh", name: "Uttar Pradesh", code: "UP" },
  { slug: "uttarakhand", name: "Uttarakhand", code: "UK" },
  { slug: "west-bengal", name: "West Bengal", code: "WB" },
  // Union Territories
  { slug: "andaman-and-nicobar-islands", name: "Andaman and Nicobar Islands", code: "AN" },
  { slug: "chandigarh", name: "Chandigarh", code: "CH" },
  { slug: "dadra-and-nagar-haveli-and-daman-and-diu", name: "Dadra and Nagar Haveli and Daman and Diu", code: "DH" },
  { slug: "delhi", name: "Delhi", code: "DL" },
  { slug: "jammu-and-kashmir", name: "Jammu and Kashmir", code: "JK" },
  { slug: "ladakh", name: "Ladakh", code: "LA" },
  { slug: "lakshadweep", name: "Lakshadweep", code: "LD" },
  { slug: "puducherry", name: "Puducherry", code: "PY" },
];

const CATEGORIES = [
  { id: 'all', label: 'All Categories' },
  { id: 'hackathon', label: 'Hackathons' },
  { id: 'conference', label: 'Conferences' },
  { id: 'workshop', label: 'Workshops' },
  { id: 'competition', label: 'Competitions' },
  { id: 'meetup', label: 'Meetups' },
];

const FORMATS = [
  { id: 'all', label: 'All Modes' },
  { id: 'in_person', label: 'In-Person' },
  { id: 'online', label: 'Online / Virtual' },
  { id: 'hybrid', label: 'Hybrid' },
];

const DATE_PRESETS = [
  { id: 'all', label: 'Any Date' },
  { id: 'this_week', label: 'This Week (7 days)' },
  { id: 'this_month', label: 'This Month (30 days)' },
  { id: 'next_90_days', label: 'Next 3 Months' },
];

export default function SearchFilters({
  filters,
  onFilterChange,
  onResetFilters,
  totalResults
}) {
  const [localQuery, setLocalQuery] = useState(filters.q || '');
  const [regions, setRegions] = useState(CANONICAL_STATES_FALLBACK);

  // Sync external filter changes
  useEffect(() => {
    setLocalQuery(filters.q || '');
  }, [filters.q]);

  // Load canonical regions from API
  useEffect(() => {
    regionService.getRegions()
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          const sorted = [...res.data].sort((a, b) => a.name.localeCompare(b.name));
          setRegions(sorted);
        }
      })
      .catch(() => {
        setRegions(CANONICAL_STATES_FALLBACK);
      });
  }, []);

  const handleSearchSubmit = (e) => {
    if (e) e.preventDefault();
    onFilterChange('q', localQuery.trim());
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearchSubmit(e);
    }
  };

  const handleClearInput = () => {
    setLocalQuery('');
    onFilterChange('q', '');
  };

  // Determine active filters for badge pills
  const activeTags = [];
  if (filters.q) {
    activeTags.push({
      key: 'q',
      label: `Keyword: "${filters.q}"`,
      onRemove: () => {
        setLocalQuery('');
        onFilterChange('q', '');
      }
    });
  }
  if (filters.state_slug && filters.state_slug !== 'all') {
    const matchedRegion = regions.find(r => r.slug === filters.state_slug);
    activeTags.push({
      key: 'state_slug',
      label: `State: ${matchedRegion?.name || filters.state_slug}`,
      onRemove: () => onFilterChange('state_slug', undefined)
    });
  }
  if (filters.category && filters.category !== 'all') {
    const cat = CATEGORIES.find(c => c.id === filters.category);
    activeTags.push({
      key: 'category',
      label: `Category: ${cat?.label || filters.category}`,
      onRemove: () => onFilterChange('category', undefined)
    });
  }
  if (filters.format && filters.format !== 'all') {
    const fmt = FORMATS.find(f => f.id === filters.format);
    activeTags.push({
      key: 'format',
      label: `Mode: ${fmt?.label || filters.format}`,
      onRemove: () => onFilterChange('format', undefined)
    });
  }
  if (filters.date_preset && filters.date_preset !== 'all') {
    const dp = DATE_PRESETS.find(d => d.id === filters.date_preset);
    activeTags.push({
      key: 'date_preset',
      label: `Date: ${dp?.label || filters.date_preset}`,
      onRemove: () => onFilterChange('date_preset', undefined)
    });
  }
  if (filters.is_free) {
    activeTags.push({
      key: 'is_free',
      label: 'Free Entry Only',
      onRemove: () => onFilterChange('is_free', undefined)
    });
  }

  const hasActiveFilters = activeTags.length > 0;

  return (
    <div className="space-y-4">
      {/* ── Main Prominent Search Bar with Dedicated Search Button ── */}
      <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row items-stretch gap-2.5">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none" />
          <input
            data-search-input
            type="text"
            value={localQuery}
            onChange={(e) => setLocalQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search events by title, topic (e.g. AI, Web3, Python, Robotics)..."
            className="w-full pl-11 pr-10 py-3 rounded-xl text-xs sm:text-sm bg-surface-50 dark:bg-surface-200 border border-border-subtle text-text-primary placeholder:text-text-muted outline-none focus:border-primary transition-colors shadow-xs min-h-[44px]"
          />

          {localQuery && (
            <button
              type="button"
              onClick={handleClearInput}
              aria-label="Clear search input"
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-md text-text-muted hover:text-text-primary transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Dedicated Search Button */}
        <button
          type="submit"
          className="btn-primary py-3 px-6 text-xs sm:text-sm font-semibold flex items-center justify-center gap-2 shadow-sm rounded-xl shrink-0 min-h-[44px] w-full sm:w-auto"
        >
          <Search className="w-4 h-4" />
          <span>Search</span>
        </button>
      </form>

      {/* ── Practical Filters Row: State/UT, Category, Mode, Date, Free Toggle ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3 items-end">
        {/* 1. Indian State or Union Territory Filter */}
        <div className="space-y-1 col-span-1">
          <label className="text-[11px] font-semibold text-text-muted flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-primary" />
            <span>State / UT</span>
          </label>
          <select
            value={filters.state_slug || 'all'}
            onChange={(e) => onFilterChange('state_slug', e.target.value === 'all' ? undefined : e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg text-xs bg-surface-50 dark:bg-surface-200 border border-border-subtle text-text-primary outline-none focus:border-primary cursor-pointer transition-colors min-h-[44px]"
          >
            <option value="all">All States & UTs</option>
            {regions.map((reg) => (
              <option key={reg.slug} value={reg.slug}>
                {reg.name} {reg.code ? `(${reg.code.replace('IN-', '')})` : ''}
              </option>
            ))}
          </select>
        </div>

        {/* 2. Category Filter */}
        <div className="space-y-1 col-span-1">
          <label className="text-[11px] font-semibold text-text-muted flex items-center gap-1">
            <Tag className="w-3.5 h-3.5 text-primary" />
            <span>Category</span>
          </label>
          <select
            value={filters.category || 'all'}
            onChange={(e) => onFilterChange('category', e.target.value === 'all' ? undefined : e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg text-xs bg-surface-50 dark:bg-surface-200 border border-border-subtle text-text-primary outline-none focus:border-primary cursor-pointer transition-colors min-h-[44px]"
          >
            {CATEGORIES.map((c) => (
              <option key={c.id} value={c.id}>
                {c.label}
              </option>
            ))}
          </select>
        </div>

        {/* 3. Online/Offline Mode Filter */}
        <div className="space-y-1 col-span-1">
          <label className="text-[11px] font-semibold text-text-muted flex items-center gap-1">
            <Globe className="w-3.5 h-3.5 text-primary" />
            <span>Mode</span>
          </label>
          <select
            value={filters.format || 'all'}
            onChange={(e) => onFilterChange('format', e.target.value === 'all' ? undefined : e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg text-xs bg-surface-50 dark:bg-surface-200 border border-border-subtle text-text-primary outline-none focus:border-primary cursor-pointer transition-colors min-h-[44px]"
          >
            {FORMATS.map((f) => (
              <option key={f.id} value={f.id}>
                {f.label}
              </option>
            ))}
          </select>
        </div>

        {/* 4. Date Filter */}
        <div className="space-y-1 col-span-1">
          <label className="text-[11px] font-semibold text-text-muted flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5 text-primary" />
            <span>Date</span>
          </label>
          <select
            value={filters.date_preset || 'all'}
            onChange={(e) => onFilterChange('date_preset', e.target.value === 'all' ? undefined : e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg text-xs bg-surface-50 dark:bg-surface-200 border border-border-subtle text-text-primary outline-none focus:border-primary cursor-pointer transition-colors min-h-[44px]"
          >
            {DATE_PRESETS.map((d) => (
              <option key={d.id} value={d.id}>
                {d.label}
              </option>
            ))}
          </select>
        </div>

        {/* 5. Free Entry Toggle & Reset */}
        <div className="col-span-1 sm:col-span-2 md:col-span-4 lg:col-span-1 flex items-center justify-between lg:justify-end gap-3 min-h-[44px] pt-1">
          <label className="flex items-center gap-2 cursor-pointer select-none text-xs text-text-secondary hover:text-text-primary">
            <input
              type="checkbox"
              checked={!!filters.is_free}
              onChange={(e) => onFilterChange('is_free', e.target.checked ? true : undefined)}
              className="w-4 h-4 rounded cursor-pointer accent-[var(--color-primary)]"
            />
            <span className="font-medium">Free Entry Only</span>
          </label>

          {hasActiveFilters && (
            <button
              type="button"
              onClick={onResetFilters}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs text-text-muted hover:text-text-primary hover:bg-surface-300 transition-colors"
              title="Reset all filters"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* ── Active Filter Tags & Results Count ── */}
      {(hasActiveFilters || totalResults !== undefined) && (
        <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-border-subtle text-xs">
          {/* Active Tags */}
          <div className="flex flex-wrap items-center gap-1.5">
            {activeTags.map((tag) => (
              <span
                key={tag.key}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium bg-surface-300 text-text-primary border border-border-subtle"
              >
                <span>{tag.label}</span>
                <button
                  type="button"
                  onClick={tag.onRemove}
                  className="p-0.5 rounded-full hover:bg-surface-400 text-text-muted hover:text-text-primary transition-colors"
                  aria-label={`Remove filter: ${tag.label}`}
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}

            {hasActiveFilters && (
              <button
                type="button"
                onClick={onResetFilters}
                className="text-[11px] font-semibold text-primary hover:underline ml-1"
              >
                Clear all
              </button>
            )}
          </div>

          {/* Results Count */}
          {totalResults !== undefined && (
            <span className="text-[11px] font-mono text-text-muted">
              {totalResults} {totalResults === 1 ? 'event' : 'events'} found
            </span>
          )}
        </div>
      )}
    </div>
  );
}
