import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Terminal, Lock, Mail, Eye, EyeOff, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid login credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md p-8 rounded-2xl border border-border-strong bg-surface-200 shadow-xl space-y-6">
        <div className="text-center space-y-2">
          <div 
            className="w-12 h-12 rounded-xl flex items-center justify-center mx-auto"
            style={{
              background: 'linear-gradient(135deg, rgba(168, 138, 255, 0.2) 0%, rgba(131, 229, 197, 0.15) 100%)',
              color: 'var(--color-primary)'
            }}
          >
            <Terminal className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-extrabold text-text-primary tracking-tight">Sign In</h2>
          <p className="text-xs text-text-secondary">
            Access unlimited event details, reminders, and saved bookmarks.
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-coral/10 border border-coral/30 text-coral text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-mono text-text-secondary block mb-1">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="developer@example.com"
                className="w-full pl-10 pr-4 py-2.5 bg-surface-100 border border-border-subtle focus:border-primary rounded-xl text-xs sm:text-sm text-text-primary placeholder:text-text-muted outline-none transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-mono text-text-secondary block mb-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-10 py-2.5 bg-surface-100 border border-border-subtle focus:border-primary rounded-xl text-xs sm:text-sm text-text-primary placeholder:text-text-muted outline-none transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-2.5 rounded-xl font-bold text-xs sm:text-sm flex items-center justify-center gap-2 mt-2"
          >
            {loading ? "Authenticating..." : "Sign In to Account"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="text-center text-xs text-text-muted">
          Don't have an account yet?{" "}
          <Link to="/register" className="text-primary hover:underline font-semibold">
            Join Free
          </Link>
        </div>
      </div>
    </div>
  );
}
