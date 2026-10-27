import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, AlertTriangle, Layers, Activity, 
  Trash2, Plus, RefreshCw, CheckCircle2, Lock, Terminal, Eye, FileText
} from 'lucide-react';
import { adminService, eventService } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function AdminDashboardPage() {
  const { isAdmin, isSuperAdmin } = useAuth();
  const [activeTab, setActiveTab] = useState('overview'); // overview, moderation, sources, bulk_delete, audit
  const [stats, setStats] = useState(null);
  const [sources, setSources] = useState([]);
  const [events, setEvents] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Bulk delete state
  const [confirmationPhrase, setConfirmationPhrase] = useState('');
  const [deleteScope, setDeleteScope] = useState('unverified');
  const [bulkDeleting, setBulkDeleting] = useState(false);
  const [bulkResult, setBulkResult] = useState(null);

  const REQUIRED_PHRASE = "DELETE ALL EVENTS PERMANENTLY";

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, sourcesRes, eventsRes, auditRes] = await Promise.all([
        adminService.getStats(),
        adminService.getSources(),
        eventService.getEvents({ page_size: 50 }),
        adminService.getAuditLogs(30)
      ]);
      setStats(statsRes.data);
      setSources(sourcesRes.data);
      setEvents(eventsRes.data.items);
      setAuditLogs(auditRes.data);
    } catch (err) {
      console.error("Failed to load admin data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      loadData();
    }
  }, [isAdmin]);

  const handleUpdateStatus = async (eventId, newStatus) => {
    try {
      await adminService.updateEvent(eventId, { verification_status: newStatus });
      setEvents(prev => prev.map(e => e.id === eventId ? { ...e, verification_status: newStatus } : e));
    } catch (err) {
      console.error("Update status error", err);
    }
  };

  const handleDeleteEvent = async (eventId) => {
    if (!window.confirm("Are you sure you want to permanently delete this listing?")) return;
    try {
      await adminService.deleteEvent(eventId);
      setEvents(prev => prev.filter(e => e.id !== eventId));
    } catch (err) {
      console.error("Delete event error", err);
    }
  };

  const handleToggleSource = async (sourceId, currentEnabled) => {
    try {
      await adminService.updateSource(sourceId, { is_enabled: !currentEnabled });
      setSources(prev => prev.map(s => s.id === sourceId ? { ...s, is_enabled: !currentEnabled } : s));
    } catch (err) {
      console.error("Toggle source error", err);
    }
  };

  const handleExecuteBulkDelete = async (e) => {
    e.preventDefault();
    if (confirmationPhrase.trim() !== REQUIRED_PHRASE) return;
    setBulkDeleting(true);
    try {
      const res = await adminService.bulkDelete({
        confirmation_phrase: confirmationPhrase.trim(),
        scope: deleteScope
      });
      setBulkResult(res.data);
      setConfirmationPhrase('');
      loadData();
    } catch (err) {
      setBulkResult({ status: 'error', message: err.response?.data?.detail || "Bulk deletion failed." });
    } finally {
      setBulkDeleting(false);
    }
  };

  if (!isAdmin) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center space-y-3">
        <Lock className="w-12 h-12 text-rose-500 mx-auto" />
        <h2 className="text-xl font-bold text-white tracking-tight">Restricted Access</h2>
        <p className="text-xs text-slate-400">
          This operational console requires elevated administrative privileges.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-border-subtle">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-mono px-2.5 py-0.5 rounded bg-surface-200 text-sky-400 border border-border-subtle">
              OPERATIONS CONSOLE
            </span>
            <span className="text-xs font-mono text-emerald-400 font-medium">Live Production Guard</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Admin & Governance Portal</h1>
        </div>

        <button
          onClick={loadData}
          className="p-2.5 rounded-xl bg-surface-100 hover:bg-surface-200 text-slate-300 flex items-center gap-2 text-xs font-medium border border-border-subtle transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-sky-400' : ''}`} />
          <span>Refresh Metrics</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto border-b border-border-subtle pb-3">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
            activeTab === 'overview'
              ? 'bg-sky-500 text-slate-950 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-surface-100'
          }`}
        >
          Operational Overview
        </button>
        <button
          onClick={() => setActiveTab('moderation')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
            activeTab === 'moderation'
              ? 'bg-sky-500 text-slate-950 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-surface-100'
          }`}
        >
          Event Moderation ({events.length})
        </button>
        <button
          onClick={() => setActiveTab('sources')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
            activeTab === 'sources'
              ? 'bg-sky-500 text-slate-950 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-surface-100'
          }`}
        >
          Discovery Sources ({sources.length})
        </button>
        <button
          onClick={() => setActiveTab('audit')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
            activeTab === 'audit'
              ? 'bg-sky-500 text-slate-950 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-surface-100'
          }`}
        >
          Security Audit Logs
        </button>
        {isSuperAdmin && (
          <button
            onClick={() => setActiveTab('bulk_delete')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              activeTab === 'bulk_delete'
                ? 'bg-rose-500 text-white shadow-sm'
                : 'text-rose-400 hover:bg-rose-500/10'
            }`}
          >
            Audited Bulk Delete
          </button>
        )}
      </div>

      {/* Tab: Overview Metrics */}
      {activeTab === 'overview' && stats && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl border border-border-subtle bg-surface-100 space-y-1">
              <span className="text-xs font-mono text-slate-400">Total Events</span>
              <p className="text-2xl font-extrabold text-white">{stats.total_published_events}</p>
              <span className="text-[11px] text-slate-400">Live in database</span>
            </div>

            <div className="p-5 rounded-2xl border border-border-subtle bg-surface-100 space-y-1">
              <span className="text-xs font-mono text-emerald-400">Verified Events</span>
              <p className="text-2xl font-extrabold text-emerald-400">{stats.verified_events}</p>
              <span className="text-[11px] text-slate-400">Full evidence checked</span>
            </div>

            <div className="p-5 rounded-2xl border border-border-subtle bg-surface-100 space-y-1">
              <span className="text-xs font-mono text-amber-400">Under Review / Unverified</span>
              <p className="text-2xl font-extrabold text-amber-400">{stats.unverified_events + stats.needs_review_events}</p>
              <span className="text-[11px] text-slate-400">Pending corroboration</span>
            </div>

            <div className="p-5 rounded-2xl border border-border-subtle bg-surface-100 space-y-1">
              <span className="text-xs font-mono text-indigo-400">Registered Sources</span>
              <p className="text-2xl font-extrabold text-indigo-400">{stats.total_sources}</p>
              <span className="text-[11px] text-slate-400">{stats.sources_with_errors} reporting errors</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl border border-border-subtle bg-surface-100 space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Activity className="w-4 h-4 text-sky-400" />
                <span>Event Lifecycle Breakdown</span>
              </h3>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between p-2.5 rounded-xl bg-surface-200">
                  <span className="text-slate-300">Upcoming Active Events</span>
                  <span className="font-mono text-emerald-400 font-bold">{stats.upcoming_events}</span>
                </div>
                <div className="flex items-center justify-between p-2.5 rounded-xl bg-surface-200">
                  <span className="text-slate-300">Expired / Registration Closed</span>
                  <span className="font-mono text-slate-400 font-bold">{stats.expired_or_closed_events}</span>
                </div>
                <div className="flex items-center justify-between p-2.5 rounded-xl bg-surface-200">
                  <span className="text-slate-300">Pending User Inaccuracy Reports</span>
                  <span className="font-mono text-amber-400 font-bold">{stats.pending_reports}</span>
                </div>
              </div>
            </div>

            <div className="p-6 rounded-2xl border border-border-subtle bg-surface-100 space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Geographic Governance Integrity</span>
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Backend queries strictly enforce venue-only physical categorization. Cross-state leakage is prohibited by automated pytest validation. Online events are tagged with format="online" and decoupled from state physical queues.
              </p>
              <div className="p-3 rounded-xl bg-surface-200 text-xs font-mono text-slate-400">
                Rule: Organizer HQ location != Physical Event Location
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab: Moderation */}
      {activeTab === 'moderation' && (
        <div className="space-y-4">
          <div className="overflow-x-auto rounded-2xl border border-border-subtle bg-surface-100">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-surface-200 text-slate-400 uppercase font-mono text-[11px] border-b border-border-subtle">
                <tr>
                  <th className="p-3.5">ID</th>
                  <th className="p-3.5">Title</th>
                  <th className="p-3.5">Location</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5">Verification</th>
                  <th className="p-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle">
                {events.map((ev) => (
                  <tr key={ev.id} className="hover:bg-surface-200/50 transition-colors">
                    <td className="p-3.5 font-mono text-slate-400">#{ev.id}</td>
                    <td className="p-3.5 font-medium text-white max-w-xs truncate">
                      <a href={`/events/${ev.slug}`} target="_blank" rel="noopener noreferrer" className="hover:text-sky-400">
                        {ev.title}
                      </a>
                    </td>
                    <td className="p-3.5 font-mono">
                      {ev.format === 'online' ? 'Online' : (ev.city ? `${ev.city}, ${ev.region?.name || ''}` : ev.region?.name || '-')}
                    </td>
                    <td className="p-3.5 font-mono capitalize">{ev.status}</td>
                    <td className="p-3.5">
                      <select
                        value={ev.verification_status}
                        onChange={(e) => handleUpdateStatus(ev.id, e.target.value)}
                        className={`text-xs font-mono px-2 py-1 rounded-lg border outline-none bg-surface-200 ${
                          ev.verification_status === 'verified'
                            ? 'text-emerald-400 border-emerald-500/30'
                            : 'text-amber-400 border-amber-500/30'
                        }`}
                      >
                        <option value="verified">Verified</option>
                        <option value="unverified">Unverified</option>
                        <option value="needs_review">Needs Review</option>
                        <option value="rejected">Rejected</option>
                      </select>
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => handleDeleteEvent(ev.id)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-surface-200 transition-colors"
                        title="Delete listing"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab: Discovery Sources */}
      {activeTab === 'sources' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sources.map((src) => (
              <div key={src.id} className="p-5 rounded-2xl border border-border-subtle bg-surface-100 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-surface-200 text-sky-400 border border-border-subtle uppercase">
                    {src.source_type}
                  </span>
                  <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${
                    src.health_status === 'healthy' ? 'badge-verified' : 'badge-unverified'
                  }`}>
                    {src.health_status}
                  </span>
                </div>

                <h3 className="font-bold text-sm text-white">{src.name}</h3>
                <p className="text-xs text-slate-400 truncate font-mono">{src.base_url}</p>

                <div className="pt-3 border-t border-border-subtle flex items-center justify-between text-xs">
                  <span className="text-slate-400 font-mono text-[11px]">
                    Interval: {src.crawl_interval_hours}h
                  </span>
                  <button
                    onClick={() => handleToggleSource(src.id, src.is_enabled)}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                      src.is_enabled ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    }`}
                  >
                    {src.is_enabled ? 'Disable' : 'Enable'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab: Audited Bulk Delete */}
      {activeTab === 'bulk_delete' && isSuperAdmin && (
        <div className="max-w-2xl mx-auto p-8 rounded-2xl border border-rose-500/30 bg-surface-100 space-y-6">
          <div className="flex items-center gap-3 text-rose-400">
            <AlertTriangle className="w-8 h-8" />
            <div>
              <h2 className="text-lg font-bold text-white">Audited Bulk Deletion Console</h2>
              <p className="text-xs text-rose-400">Super-Administrator Exclusive Action</p>
            </div>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            This operation irrevocably removes event records from the database. It will preserve source registries, user accounts, and administrative configuration. An immutable security audit entry will be logged with your identity and IP address.
          </p>

          <form onSubmit={handleExecuteBulkDelete} className="space-y-4">
            <div>
              <label className="text-xs font-mono text-slate-400 block mb-1">Deletion Scope</label>
              <select
                value={deleteScope}
                onChange={(e) => setDeleteScope(e.target.value)}
                className="w-full p-2.5 bg-surface-200 border border-border-subtle rounded-xl text-xs text-white"
              >
                <option value="unverified">Delete Only Unverified Candidates</option>
                <option value="all">Delete All Discovered Events Permanently</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-mono text-slate-400 block mb-1">
                To confirm, type <strong className="text-rose-400 font-mono select-all">{REQUIRED_PHRASE}</strong>:
              </label>
              <input
                type="text"
                required
                value={confirmationPhrase}
                onChange={(e) => setConfirmationPhrase(e.target.value)}
                placeholder={REQUIRED_PHRASE}
                className="w-full p-2.5 bg-surface-200 border border-rose-500/40 rounded-xl text-xs text-white font-mono outline-none focus:border-rose-400"
              />
            </div>

            {bulkResult && (
              <div className={`p-3 rounded-lg text-xs ${bulkResult.status === 'success' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                {bulkResult.message}
              </div>
            )}

            <button
              type="submit"
              disabled={bulkDeleting || confirmationPhrase.trim() !== REQUIRED_PHRASE}
              className="w-full py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 disabled:opacity-40 text-white font-bold text-xs transition-colors shadow-sm"
            >
              {bulkDeleting ? 'Executing Audited Bulk Action...' : 'Confirm & Execute Permanent Bulk Deletion'}
            </button>
          </form>
        </div>
      )}

      {/* Tab: Security Audit Logs */}
      {activeTab === 'audit' && (
        <div className="space-y-4">
          <div className="overflow-x-auto rounded-2xl border border-border-subtle bg-surface-100">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-surface-200 text-slate-400 uppercase font-mono text-[11px] border-b border-border-subtle">
                <tr>
                  <th className="p-3.5">Timestamp</th>
                  <th className="p-3.5">Action</th>
                  <th className="p-3.5">Target</th>
                  <th className="p-3.5">IP Address</th>
                  <th className="p-3.5">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle font-mono text-xs">
                {auditLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-surface-200/50 transition-colors">
                    <td className="p-3.5 text-slate-400">{new Date(log.created_at).toLocaleString()}</td>
                    <td className="p-3.5 text-sky-400 font-semibold">{log.action}</td>
                    <td className="p-3.5 text-slate-300">{log.resource_type} {log.resource_id ? `#${log.resource_id}` : ''}</td>
                    <td className="p-3.5 text-slate-400">{log.ip_address || 'Internal'}</td>
                    <td className="p-3.5 text-slate-400 truncate max-w-xs">{log.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
