import React from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import { Lock, Sparkles, X, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function ViewLimitModal() {
  const { viewLimitModalOpen, setViewLimitModalOpen, viewLimitInfo } = useAuth();

  return (
    <AnimatePresence>
      {viewLimitModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.94, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.94, y: 8 }}
            transition={{ duration: 0.18, ease: 'easeOut' }}
            className="relative w-full max-w-md p-6 sm:p-7 rounded-2xl shadow-2xl bg-surface-200 border border-border-strong text-text-primary"
          >
            <button
              onClick={() => setViewLimitModalOpen(false)}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-300 transition-colors"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>

            <div 
              className="w-11 h-11 rounded-xl flex items-center justify-center mb-4"
              style={{
                backgroundColor: 'var(--color-primary-subtle)',
                color: 'var(--color-primary)',
                border: '1px solid rgba(168, 138, 255, 0.3)'
              }}
            >
              <Lock className="w-5 h-5" />
            </div>

            <h3 className="text-lg font-bold mb-2 tracking-tight text-text-primary">
              {viewLimitInfo?.message || "Free Browsing Allowance Reached"}
            </h3>

            <p className="text-xs leading-relaxed mb-4 text-text-secondary">
              You've explored <strong>5 verified events</strong> as an anonymous guest. To maintain platform integrity and access saved bookmarks, deadline alerts, and unlimited views, please sign in or create a free account.
            </p>

            <div className="p-3.5 rounded-xl mb-5 text-xs space-y-1.5 bg-surface-100 border border-border-subtle">
              <div className="flex items-center gap-1.5 font-semibold text-mint">
                <ShieldCheck className="w-4 h-4" />
                <span>100% Free for Developers & Students</span>
              </div>
              <p className="text-[11px] text-text-muted">
                Accounts grant unlimited event inspections, verified registration links, and full AI discovery context.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Link
                to="/login"
                onClick={() => setViewLimitModalOpen(false)}
                className="btn-secondary text-center text-xs py-2.5 rounded-xl"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                onClick={() => setViewLimitModalOpen(false)}
                className="btn-primary text-center text-xs py-2.5 rounded-xl flex items-center justify-center gap-1.5 font-bold"
              >
                <span>Join Free</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
