import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Calendar, MapPin, Globe, ShieldCheck, 
  AlertTriangle, Bookmark, ArrowRight, Clock, 
  ExternalLink, Sparkles
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { authService } from '../../services/api';
import { getRegistrationAction, getInternalEventRoute } from '../../utils/navigation';

export default function EventCard({ 
  event, 
  featured = false,
  featuredVariant = 1,
  variantIndex = 0,
  cardIndex,
  onBookmarkChanged 
}) {
  const { isAuthenticated } = useAuth();
  const [isSaved, setIsSaved] = useState(event.is_saved || false);
  const [saving, setSaving] = useState(false);

  const handleBookmarkToggle = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isAuthenticated) {
      window.dispatchEvent(new CustomEvent('eh:view-limit-reached', {
        detail: { message: "Sign in to save opportunities and track deadlines." }
      }));
      return;
    }

    setSaving(true);
    try {
      if (isSaved) {
        await authService.unsaveEvent(event.id);
        setIsSaved(false);
      } else {
        await authService.saveEvent({ event_id: event.id });
        setIsSaved(true);
      }
      if (onBookmarkChanged) onBookmarkChanged(event.id, !isSaved);
    } catch (err) {
      console.error("Bookmark error", err);
    } finally {
      setSaving(false);
    }
  };

  const isVerified = event.verification_status === 'verified';
  const isOnline = event.format === 'online';
  const locationLabel = isOnline 
    ? 'Online / Virtual'
    : event.city && event.region?.name 
      ? `${event.city}, ${event.region.name}` 
      : event.city || event.region?.name || 'India';

  const isClosed = event.status === 'closed' || 
    (event.registration_deadline && new Date(event.registration_deadline) < new Date());

  const formattedDate = new Date(event.start_date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });

  const deadlineFormatted = event.registration_deadline
    ? new Date(event.registration_deadline).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    : null;

  const internalUrl = getInternalEventRoute(event);
  const regAction = getRegistrationAction(event);

  // Determine solid background variant (0: terracotta/burgundy, 1: forest green, 2: warm gold, 3: rose)
  const variant = (((cardIndex !== undefined ? cardIndex : event.id) ?? variantIndex) % 4);
  const cardClass = featured 
    ? (featuredVariant === 1 ? 'eh-card-featured-1 p-6' : 'eh-card-featured-2 p-6')
    : `eh-card-variant-${variant} p-5`;

  return (
    <article 
      className={`${cardClass} flex flex-col justify-between min-w-0 group relative`}
    >
      <div className="min-w-0">
        {/* Top Metadata: Category, Mode, Verification, Bookmark */}
        <div className="flex items-center justify-between gap-2 mb-3 min-w-0">
          <div className="flex items-center gap-1.5 flex-wrap min-w-0">
            {/* Category badge */}
            <span 
              className="text-[11px] font-mono font-bold uppercase px-2.5 py-0.5 rounded-md tracking-wider bg-surface-100 text-text-primary border border-border-subtle"
            >
              {event.category}
            </span>

            {/* Mode badge */}
            <span className="badge-format text-[11px] font-mono px-2 py-0.5 rounded-md flex items-center gap-1">
              {isOnline ? <Globe className="w-3 h-3 text-green" /> : <MapPin className="w-3 h-3 text-primary" />}
              <span className="capitalize">{event.format.replace('_', ' ')}</span>
            </span>

            {featured && (
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md flex items-center gap-1 bg-gold/20 text-gold border border-gold/30">
                <Sparkles className="w-3 h-3 fill-current" />
                <span>Featured</span>
              </span>
            )}
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            {/* Verification Status */}
            {isVerified ? (
              <span className="badge-verified text-[11px] font-semibold px-2 py-0.5 rounded-md flex items-center gap-1" title="Verified listing">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Verified</span>
              </span>
            ) : (
              <span className="badge-unverified text-[11px] font-semibold px-2 py-0.5 rounded-md flex items-center gap-1" title="Community review candidate">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Under Review</span>
              </span>
            )}

            {/* Bookmark */}
            <button
              onClick={handleBookmarkToggle}
              disabled={saving}
              aria-label={isSaved ? "Remove from bookmarks" : "Save event"}
              className="p-1.5 rounded-md transition-colors bg-surface-100 border border-border-subtle text-text-muted hover:text-text-primary"
              title={isSaved ? "Saved" : "Save"}
            >
              <Bookmark className={`w-3.5 h-3.5 ${isSaved ? 'fill-current text-primary' : ''}`} />
            </button>
          </div>
        </div>

        {/* Event Title */}
        <Link to={internalUrl} className="block mb-2 group-hover:text-primary transition-colors">
          <h3 
            className={`font-bold leading-snug line-clamp-2 text-text-primary ${featured ? 'text-lg sm:text-xl' : 'text-sm sm:text-base'}`}
          >
            {event.title}
          </h3>
        </Link>

        {/* Date and Location */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs text-text-secondary gap-2 mb-3">
          <div className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-green shrink-0" />
            <span className="font-semibold text-text-primary">{formattedDate}</span>
          </div>

          <div className="flex items-center gap-1.5" title={locationLabel}>
            <MapPin className="w-3.5 h-3.5 text-primary shrink-0" />
            <span className="truncate max-w-[200px]">{locationLabel}</span>
          </div>
        </div>

        {/* Registration Deadline (When Available) */}
        {deadlineFormatted && (
          <div 
            className="flex items-center gap-1.5 text-[11px] font-mono mb-3.5"
            style={{ color: isClosed ? 'var(--color-text-muted)' : 'var(--color-gold)' }}
          >
            <Clock className="w-3.5 h-3.5 shrink-0" />
            <span>{isClosed ? 'Deadline Passed: ' : 'Registration Closes: '}{deadlineFormatted}</span>
          </div>
        )}
      </div>

      {/* Card Footer: Clear View Details Action & Safe Registration Action */}
      <div 
        className="pt-3 border-t border-border-subtle flex items-center justify-between gap-3 min-w-0"
      >
        <div className="flex items-center gap-2 text-xs">
          {event.is_free ? (
            <span className="font-mono text-[11px] font-bold text-green">
              Free Entry
            </span>
          ) : event.prize_pool ? (
            <span className="font-mono text-[11px] font-semibold text-gold truncate max-w-[130px]">
              {event.prize_pool}
            </span>
          ) : (
            <span className="font-mono text-[11px] text-text-muted">
              Standard
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Link
            to={internalUrl}
            className="inline-flex items-center gap-1 text-xs font-semibold text-text-secondary hover:text-text-primary transition-colors"
          >
            <span>View Details</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>

          {regAction.type === 'closed' ? (
            <span className="text-[11px] font-mono px-2 py-1 rounded bg-surface-100 text-text-muted border border-border-subtle">
              Closed
            </span>
          ) : regAction.type === 'cancelled' ? (
            <span className="text-[11px] font-mono px-2 py-1 rounded bg-surface-100 text-rose border border-rose/30">
              Cancelled
            </span>
          ) : regAction.type === 'external' ? (
            <a
              href={regAction.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="btn-primary text-xs py-1 px-3 flex items-center gap-1 font-semibold"
              title="Official Registration Page"
            >
              <span>Register</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          ) : null}
        </div>
      </div>
    </article>
  );
}
