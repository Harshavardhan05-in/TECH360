import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  Calendar, MapPin, Globe, Award, ShieldCheck, 
  AlertTriangle, Bookmark, ExternalLink, ArrowLeft, 
  Users, CheckCircle2, Clock, Flag, Share2, Info, ChevronRight,
  RefreshCw, Check, AlertCircle, Building2, Sparkles, X
} from 'lucide-react';
import { eventService, authService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { getSafeUrl, isRegistrationUrlReachable, getRegistrationAction } from '../utils/navigation';

export default function EventDetailPage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSaved, setIsSaved] = useState(false);
  const [verifyingLink, setVerifyingLink] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);

  // Report Modal state
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [reportPayload, setReportPayload] = useState({ issue_type: 'broken_link', description: '' });
  const [reportSubmitted, setReportSubmitted] = useState(false);

  useEffect(() => {
    setLoading(true);
    eventService.getEventDetail(slug)
      .then((res) => {
        setEvent(res.data);
        setIsSaved(res.data.is_saved);
      })
      .catch((err) => {
        if (err.response?.status === 403 && err.response?.data?.detail?.view_limit_reached) {
          setError("Free browsing limit reached. Please sign in or join free to view full event details.");
        } else {
          setError(err.response?.data?.detail || "Event listing not found.");
        }
      })
      .finally(() => setLoading(false));
  }, [slug]);

  const handleBookmark = async () => {
    if (!isAuthenticated) {
      window.dispatchEvent(new CustomEvent('eh:view-limit-reached', {
        detail: { message: "Sign in to save this event and track deadlines." }
      }));
      return;
    }
    try {
      if (isSaved) {
        await authService.unsaveEvent(event.id);
        setIsSaved(false);
      } else {
        await authService.saveEvent({ event_id: event.id });
        setIsSaved(true);
      }
    } catch (err) {
      console.error("Bookmark error", err);
    }
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  const handleLiveVerifyLink = async () => {
    if (!event || verifyingLink) return;
    setVerifyingLink(true);
    try {
      const res = await eventService.verifyLink(event.id);
      setEvent(prev => ({
        ...prev,
        link_status: res.data.link_status,
        link_http_status: res.data.link_http_status,
        link_last_checked_at: res.data.link_last_checked_at,
        link_error: res.data.link_error,
      }));
    } catch (err) {
      console.error("Failed to verify link in real time", err);
    } finally {
      setVerifyingLink(false);
    }
  };

  const handleReportSubmit = async (e) => {
    e.preventDefault();
    try {
      await eventService.reportEvent(event.id, reportPayload);
      setReportSubmitted(true);
      setTimeout(() => {
        setReportModalOpen(false);
        setReportSubmitted(false);
      }, 2000);
    } catch (err) {
      console.error("Report submit error", err);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-6 animate-pulse">
        <div className="h-4 w-40 bg-surface-300 rounded" />
        <div className="rounded-2xl border border-border-subtle bg-surface-200 p-8 space-y-4">
          <div className="h-6 w-32 bg-surface-300 rounded" />
          <div className="h-10 w-3/4 bg-surface-300 rounded" />
          <div className="h-4 w-1/2 bg-surface-300 rounded" />
        </div>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-gold/10 border border-gold/30 text-gold flex items-center justify-center mx-auto">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-text-primary">Event Not Found</h2>
        <p className="text-xs text-text-secondary leading-relaxed max-w-sm mx-auto">
          {error || "The requested event record does not exist or may have been moved."}
        </p>
        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            onClick={() => window.history.length > 1 ? navigate(-1) : navigate('/')}
            className="btn-secondary text-xs inline-flex items-center gap-1.5"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Go Back</span>
          </button>
          <Link
            to="/"
            className="btn-primary text-xs inline-flex items-center gap-1.5"
          >
            <span>Browse All Events</span>
          </Link>
        </div>
      </div>
    );
  }

  const isVerified = event.verification_status === 'verified';
  const isCancelled = event.status === 'cancelled';
  const isClosed = event.status === 'closed' || (event.registration_deadline && new Date(event.registration_deadline) < new Date());

  const startFormatted = new Date(event.start_date).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
  const endFormatted = new Date(event.end_date).toLocaleDateString('en-US', {
    weekday: 'short',
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
    : "Ongoing / Open until capacity";

  const isRegReachable = isRegistrationUrlReachable(event);
  const linkStatus = event.link_status || 'unverified';
  const isLinkConfirmed = isRegReachable && (linkStatus === 'confirmed_reachable' || linkStatus === 'redirected');
  const isLinkNotFound = linkStatus === 'confirmed_not_found' || event.link_http_status === 404;
  const isLinkUnverified = !isRegReachable && !isLinkNotFound && !isClosed;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
      {/* Back button and Breadcrumb navigation */}
      <div className="flex items-center gap-2 text-xs text-text-muted">
        <button
          type="button"
          onClick={() => window.history.length > 1 ? navigate(-1) : navigate('/')}
          className="inline-flex items-center gap-1 text-xs font-semibold text-text-secondary hover:text-text-primary transition-colors pr-3 border-r border-border-subtle shrink-0"
          title="Back to previous page"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back</span>
        </button>

        <nav aria-label="Breadcrumb" className="flex items-center space-x-2 truncate">
          <Link to="/" className="hover:text-text-primary transition-colors shrink-0">Discover</Link>
          <ChevronRight className="w-3.5 h-3.5 shrink-0" />
          {event.region ? (
            <>
              <Link to={`/india/${event.region.slug}`} className="hover:text-text-primary transition-colors shrink-0">
                {event.region.name}
              </Link>
              <ChevronRight className="w-3.5 h-3.5 shrink-0" />
            </>
          ) : (
            <>
              <Link to="/global" className="hover:text-text-primary transition-colors shrink-0">Global</Link>
              <ChevronRight className="w-3.5 h-3.5 shrink-0" />
            </>
          )}
          <span className="text-text-secondary truncate">{event.title}</span>
        </nav>
      </div>

      {/* ── Large, Attractive Colourful Banner ── */}
      <div 
        className="eh-card-featured-1 p-6 sm:p-8 space-y-6 relative overflow-hidden shadow-sm"
      >
        <div className="space-y-4">
          {/* Top Badges */}
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="badge-format text-xs font-mono px-2.5 py-0.5 rounded-md uppercase font-semibold">
                {event.format.replace('_', ' ')}
              </span>
              <span 
                className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-md uppercase"
                style={{ backgroundColor: 'var(--color-primary-subtle)', color: 'var(--color-primary)' }}
              >
                {event.category}
              </span>

              {/* Status Badge: Verified, Unverified, or Closed */}
              {isClosed ? (
                <span className="text-xs font-medium px-2.5 py-0.5 rounded-md bg-surface-300 text-text-muted border border-border-subtle flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Registration Closed</span>
                </span>
              ) : isVerified ? (
                <span className="text-xs font-medium px-2.5 py-0.5 rounded-md badge-verified flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Verified Listing</span>
                </span>
              ) : (
                <span className="text-xs font-medium px-2.5 py-0.5 rounded-md badge-unverified flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Unverified Candidate</span>
                </span>
              )}
            </div>

            {/* Bookmark & Share Actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={handleBookmark}
                className="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1.5"
              >
                <Bookmark className={`w-3.5 h-3.5 ${isSaved ? 'fill-current text-primary' : ''}`} />
                <span>{isSaved ? 'Saved' : 'Save'}</span>
              </button>

              <button
                onClick={handleCopyLink}
                className="p-1.5 rounded-lg btn-secondary text-xs"
                title="Copy event link"
              >
                {copiedLink ? <Check className="w-3.5 h-3.5 text-mint" /> : <Share2 className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

          {/* Title */}
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-text-primary leading-tight">
            {event.title}
          </h1>

          {/* Organizer */}
          <div className="flex items-center gap-2 text-xs text-text-secondary flex-wrap">
            <span>Hosted by</span>
            <strong className="text-text-primary font-semibold">{event.organizer?.name || 'Verified Tech Organizer'}</strong>
            {event.organizer?.official_website && (
              <a
                href={event.organizer.official_website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline inline-flex items-center gap-1 font-medium ml-1"
              >
                <span>Organizer Website</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        </div>

        {/* ── Key Highlights Strip ── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6 border-t border-border-subtle">
          <div className="space-y-1">
            <span className="text-[10px] font-mono uppercase text-text-muted flex items-center gap-1">
              <Calendar className="w-3 h-3 text-mint" />
              <span>Event Date</span>
            </span>
            <p className="text-xs font-bold text-text-primary">{startFormatted}</p>
            {event.end_date && event.end_date !== event.start_date && (
              <p className="text-[10px] text-text-muted">to {endFormatted}</p>
            )}
          </div>

          <div className="space-y-1">
            <span className="text-[10px] font-mono uppercase text-text-muted flex items-center gap-1">
              <Clock className="w-3 h-3 text-amber" />
              <span>Deadline</span>
            </span>
            <p className="text-xs font-bold text-text-primary">{deadlineFormatted}</p>
            {isClosed && (
              <span className="text-[10px] text-coral font-medium">Closed</span>
            )}
          </div>

          <div className="space-y-1">
            <span className="text-[10px] font-mono uppercase text-text-muted flex items-center gap-1">
              <MapPin className="w-3 h-3 text-coral" />
              <span>Location</span>
            </span>
            <p className="text-xs font-bold text-text-primary">
              {event.format === 'online' ? 'Global Virtual' : (event.city || event.region?.name || 'India')}
            </p>
            <p className="text-[10px] text-text-muted">
              {event.format === 'online' ? 'Online / Remote' : (event.region?.name || 'In-Person')}
            </p>
          </div>

          <div className="space-y-1">
            <span className="text-[10px] font-mono uppercase text-text-muted flex items-center gap-1">
              <Award className="w-3 h-3 text-primary" />
              <span>Cost / Prize</span>
            </span>
            <p className="text-xs font-bold text-mint">
              {event.is_free ? 'Free Entry' : (event.prize_pool || 'Paid Entry')}
            </p>
            {event.prize_pool && (
              <p className="text-[10px] text-text-muted">Pool: {event.prize_pool}</p>
            )}
          </div>
        </div>

        {/* ── Registration URL Status & Action Buttons ── */}
        <div className="pt-6 border-t border-border-subtle flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="space-y-1 text-center sm:text-left">
            <div className="flex items-center justify-center sm:justify-start gap-1.5 text-xs font-medium text-text-secondary">
              <ShieldCheck className="w-4 h-4 text-mint shrink-0" />
              <span>Registration Reachability</span>
              {isLinkConfirmed ? (
                <span className="text-[10px] font-mono text-mint font-bold ml-1">● Confirmed Reachable (200 OK)</span>
              ) : isLinkNotFound ? (
                <span className="text-[10px] font-mono text-coral font-bold ml-1">● Link Unavailable (404)</span>
              ) : !event.registration_url ? (
                <span className="text-[10px] font-mono text-amber font-bold ml-1">● Direct Link Not Provided</span>
              ) : (
                <span className="text-[10px] font-mono text-amber font-bold ml-1">● Verification Pending</span>
              )}
            </div>
            <p className="text-[11px] text-text-muted max-w-md">
              {isCancelled
                ? 'This event was marked cancelled by the organizer.'
                : isClosed
                ? 'The registration deadline has passed.'
                : isLinkNotFound || !event.registration_url
                ? 'Registration link unavailable. View event details for more information.'
                : 'Verified official registration portal provided by the event organizer.'}
            </p>
          </div>

          <div className="flex items-center gap-2.5 w-full sm:w-auto justify-end">
            {/* Live Link Verification Button */}
            {event.registration_url && (
              <button
                onClick={handleLiveVerifyLink}
                disabled={verifyingLink}
                title="Test destination reachability in real time"
                className="p-2.5 rounded-xl btn-secondary text-xs shrink-0"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${verifyingLink ? 'animate-spin text-primary' : ''}`} />
              </button>
            )}

            {/* Action Button: Safe External or Organizer Portal */}
            {isCancelled ? (
              <div className="px-5 py-2.5 rounded-xl bg-surface-300 text-coral text-xs font-semibold cursor-not-allowed border border-coral/30">
                Event Cancelled
              </div>
            ) : isClosed ? (
              <div className="px-5 py-2.5 rounded-xl bg-surface-300 text-text-muted text-xs font-semibold cursor-not-allowed border border-border-subtle">
                Registration Closed
              </div>
            ) : isRegReachable ? (
              <a
                href={getSafeUrl(event.registration_url)}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary text-xs sm:text-sm py-2.5 px-6 font-bold shadow-lg flex items-center justify-center gap-2"
                title="Open Official Registration Portal"
              >
                <span>Register Now</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            ) : event.official_website ? (
              <a
                href={getSafeUrl(event.official_website)}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary text-xs sm:text-sm py-2.5 px-5 font-semibold flex items-center justify-center gap-2"
                title="Visit Official Organizer Website"
              >
                <span>Visit Organizer Site</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            ) : (
              <div className="px-4 py-2 rounded-xl bg-surface-300 text-text-muted text-xs font-medium">
                Registration link unavailable
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Status Alerts: Broken Link / Unverified Destination ── */}
      {isLinkNotFound && !isClosed && !isCancelled && (
        <div className="p-4 rounded-xl border border-coral/30 bg-coral/10 flex items-start gap-3 text-xs text-text-secondary">
          <AlertCircle className="w-4 h-4 text-coral shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <h4 className="font-bold text-coral">Notice: Registration Link Unavailable</h4>
            <p className="text-[11px] leading-relaxed">
              Registration link unavailable. View event details for more information.
              The previously published registration destination returned an error (HTTP 404). To prevent sending users to broken pages, EventHorizon AI has disabled the direct link. Please refer to the verified organizer details below or report an updated link.
            </p>
          </div>
        </div>
      )}

      {isLinkUnverified && !isClosed && !isCancelled && !isLinkNotFound && (
        <div className="p-4 rounded-xl border border-amber/30 bg-amber/10 flex items-start gap-3 text-xs text-text-secondary">
          <AlertTriangle className="w-4 h-4 text-amber shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <h4 className="font-bold text-amber">Notice: Unverified External Registration Destination</h4>
            <p className="text-[11px] leading-relaxed">
              This registration destination has not yet been audited by our crawler or the host requires authentication. Always ensure you are on the organizer’s official domain before entering personal information.
            </p>
          </div>
        </div>
      )}

      {/* ── Essential Event Information (Focused and Easy to Scan) ── */}
      <div className="eh-card p-6 sm:p-8 space-y-6">
        {/* Description */}
        <div className="space-y-2">
          <h2 className="text-sm font-bold text-text-primary uppercase font-mono tracking-wider">
            About This Opportunity
          </h2>
          <p className="text-xs sm:text-sm text-text-secondary leading-relaxed whitespace-pre-line">
            {event.description}
          </p>
        </div>

        {/* Tech tags */}
        {event.tags && (
          <div className="pt-4 border-t border-border-subtle space-y-2">
            <span className="text-[10px] font-mono uppercase text-text-muted block">Focus Areas & Technologies</span>
            <div className="flex flex-wrap gap-1.5">
              {event.tags.split(',').map((t, idx) => (
                <span 
                  key={idx}
                  className="text-xs font-mono px-2.5 py-1 rounded-lg bg-surface-100 border border-border-subtle text-text-secondary"
                >
                  #{t.trim()}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Venue Information (for physical events) */}
        {event.format !== 'online' && (
          <div className="pt-4 border-t border-border-subtle space-y-2">
            <h3 className="text-xs font-bold font-mono uppercase text-text-muted flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-coral" />
              <span>Physical Venue & Location</span>
            </h3>
            <div className="p-3.5 rounded-xl bg-surface-100 border border-border-subtle text-xs space-y-1">
              <p className="font-semibold text-text-primary">{event.venue_name || 'Venue details confirmed by organizer'}</p>
              <p className="text-text-muted">{event.venue_address || `${event.city || ''}, ${event.region?.name || ''}, India`}</p>
              {event.region && (
                <p className="text-[11px] text-text-muted pt-1">
                  Indian State: <Link to={`/india/${event.region.slug}`} className="text-primary hover:underline">{event.region.name}</Link>
                </p>
              )}
            </div>
          </div>
        )}

        {/* Eligibility & Team Info */}
        <div className="pt-4 border-t border-border-subtle space-y-2">
          <h3 className="text-xs font-bold font-mono uppercase text-text-muted flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-primary" />
            <span>Eligibility & Participation</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="p-3.5 rounded-xl bg-surface-100 border border-border-subtle space-y-0.5">
              <span className="text-[10px] font-mono text-text-muted block">Who Can Participate</span>
              <span className="font-medium text-text-primary">{event.eligibility || 'Open to all student and professional developers'}</span>
            </div>
            <div className="p-3.5 rounded-xl bg-surface-100 border border-border-subtle space-y-0.5">
              <span className="text-[10px] font-mono text-text-muted block">Team Formation</span>
              <span className="font-medium text-text-primary">
                {event.team_size_min && event.team_size_max 
                  ? (event.team_size_min === event.team_size_max ? `${event.team_size_min} member(s)` : `${event.team_size_min} to ${event.team_size_max} members`)
                  : 'Individual or team participation'}
              </span>
            </div>
          </div>
        </div>

        {/* Report inaccurate information */}
        <div className="pt-4 border-t border-border-subtle flex items-center justify-between text-xs text-text-muted">
          <span>Noticed an incorrect date, broken link, or inaccurate detail?</span>
          <button
            onClick={() => setReportModalOpen(true)}
            className="flex items-center gap-1 text-coral hover:underline font-medium"
          >
            <Flag className="w-3 h-3" />
            <span>Report inaccuracy</span>
          </button>
        </div>
      </div>

      {/* Report Modal */}
      {reportModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-md rounded-2xl bg-surface-200 border border-border-strong p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-text-primary">Report Event Inaccuracy</h3>
              <button onClick={() => setReportModalOpen(false)} className="text-text-muted hover:text-text-primary">
                <X className="w-4 h-4" />
              </button>
            </div>

            {reportSubmitted ? (
              <div className="text-center py-6 text-mint space-y-1">
                <CheckCircle2 className="w-8 h-8 mx-auto" />
                <p className="font-bold text-xs">Report Submitted</p>
                <p className="text-[11px] text-text-muted">Thank you for helping keep EventHorizon AI accurate.</p>
              </div>
            ) : (
              <form onSubmit={handleReportSubmit} className="space-y-3 text-xs">
                <div>
                  <label className="block text-text-secondary mb-1">Issue Type</label>
                  <select
                    value={reportPayload.issue_type}
                    onChange={(e) => setReportPayload({ ...reportPayload, issue_type: e.target.value })}
                    className="w-full p-2.5 rounded-lg bg-surface-100 border border-border-subtle text-text-primary outline-none"
                  >
                    <option value="broken_link">Broken / 404 Registration Link</option>
                    <option value="wrong_dates">Incorrect Event Dates or Deadlines</option>
                    <option value="wrong_location">Incorrect Physical Venue or State</option>
                    <option value="cancelled_event">Event Has Been Cancelled</option>
                    <option value="other">Other Inaccuracy</option>
                  </select>
                </div>

                <div>
                  <label className="block text-text-secondary mb-1">Description / Proof</label>
                  <textarea
                    rows={3}
                    required
                    value={reportPayload.description}
                    onChange={(e) => setReportPayload({ ...reportPayload, description: e.target.value })}
                    placeholder="Provide details or official organizer correction link..."
                    className="w-full p-2.5 rounded-lg bg-surface-100 border border-border-subtle text-text-primary outline-none"
                  />
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setReportModalOpen(false)}
                    className="btn-secondary text-xs"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-primary text-xs"
                  >
                    Submit Report
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
