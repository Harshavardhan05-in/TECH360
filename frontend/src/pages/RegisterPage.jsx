import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Terminal, Lock, Mail, User, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await register(email, password, fullName);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed. Please check inputs.");
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
              background: 'linear-gradient(135deg, rgba(131, 229, 197, 0.2) 0%, rgba(168, 138, 255, 0.15) 100%)',
              color: 'var(--color-mint)'
            }}
          >
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-extrabold text-text-primary tracking-tight">Create Free Account</h2>
          <p className="text-xs text-text-secondary">
            Unlimited verified event discovery, bookmarking, and deadline tracking.
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-coral/10 border border-coral/30 text-coral text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-mono text-text-secondary block mb-1">Full Name</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Ada Lovelace"
                className="w-full pl-10 pr-4 py-2.5 bg-surface-100 border border-border-subtle focus:border-primary rounded-xl text-xs sm:text-sm text-text-primary placeholder:text-text-muted outline-none transition-colors"
              />
            </div>
          </div>

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
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimum 8 characters"
                className="w-full pl-10 pr-4 py-2.5 bg-surface-100 border border-border-subtle focus:border-primary rounded-xl text-xs sm:text-sm text-text-primary placeholder:text-text-muted outline-none transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-2.5 rounded-xl font-bold text-xs sm:text-sm flex items-center justify-center gap-2 mt-2"
          >
            {loading ? "Creating Developer Profile..." : "Create Free Account"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="text-center text-xs text-text-muted">
          Already have an account?{" "}
          <Link to="/login" className="text-primary hover:underline font-semibold">
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
