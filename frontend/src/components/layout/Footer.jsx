import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, MapPin, Globe, AlertCircle } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="mt-16 border-t border-border-subtle bg-surface-200 pb-16 md:pb-0 transition-colors">
      <div className="max-w-[1280px] mx-auto px-4 sm:px-6 py-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand Info */}
          <div className="space-y-3 sm:col-span-2 lg:col-span-1">
            <div className="flex items-center gap-2">
              <div 
                className="w-6 h-6 rounded-md flex items-center justify-center font-bold text-xs bg-primary text-background"
              >
                EH
              </div>
              <span className="font-bold text-sm text-text-primary">EventHorizon AI</span>
            </div>
            <p className="text-xs leading-relaxed text-text-secondary">
              Production-oriented tech event discovery for developers, students, and engineers seeking authentic hackathons, conferences, and competitions.
            </p>
            <div className="flex items-center gap-1.5 text-[11px] font-mono text-green">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Evidence-based verification</span>
            </div>
          </div>

          {/* India Regional */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-1.5 text-text-primary">
              <MapPin className="w-3.5 h-3.5 text-primary" />
              <span>India Tech Hubs</span>
            </h4>
            <ul className="space-y-2 text-xs text-text-secondary">
              <li><Link to="/india/telangana" className="hover:text-text-primary transition-colors">Telangana (Hyderabad)</Link></li>
              <li><Link to="/india/karnataka" className="hover:text-text-primary transition-colors">Karnataka (Bengaluru)</Link></li>
              <li><Link to="/india/delhi" className="hover:text-text-primary transition-colors">Delhi NCR</Link></li>
              <li><Link to="/india/maharashtra" className="hover:text-text-primary transition-colors">Maharashtra (Mumbai)</Link></li>
              <li><Link to="/india" className="font-semibold text-primary hover:underline transition-colors">All 28 States & 8 UTs →</Link></li>
            </ul>
          </div>

          {/* Categories */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-1.5 text-text-primary">
              <Globe className="w-3.5 h-3.5 text-green" />
              <span>Explore Categories</span>
            </h4>
            <ul className="space-y-2 text-xs text-text-secondary">
              <li><Link to="/?category=hackathon" className="hover:text-text-primary transition-colors">Hackathons</Link></li>
              <li><Link to="/global" className="hover:text-text-primary transition-colors">Online & Virtual Events</Link></li>
              <li><Link to="/?category=conference" className="hover:text-text-primary transition-colors">Technical Conferences</Link></li>
              <li><Link to="/?category=workshop" className="hover:text-text-primary transition-colors">Developer Workshops</Link></li>
            </ul>
          </div>

          {/* Trust */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider mb-3 flex items-center gap-1.5 text-text-primary">
              <ShieldCheck className="w-3.5 h-3.5 text-green" />
              <span>Trust & Integrity</span>
            </h4>
            <p className="text-xs leading-relaxed mb-3 text-text-secondary">
              Every listing links directly to its official source. Online events are isolated from physical state queues.
            </p>
            <div className="p-2.5 rounded-lg text-[11px] flex items-start gap-2 bg-surface-100 border border-border-subtle text-text-muted">
              <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5 text-gold" />
              <span>Noticed an issue? Use "Report Inaccuracy" on any event page.</span>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-5 flex flex-col sm:flex-row items-center justify-between text-xs gap-2 border-t border-border-subtle text-text-muted">
          <p>© 2026 EventHorizon AI. Verified public developer data.</p>
          <div className="flex items-center gap-3 font-mono text-[11px]">
            <span>API v1.0</span>
            <span>•</span>
            <span className="text-green">Zero Hallucination Policy</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
