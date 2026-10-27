import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Compass, MapPin, Globe, Bookmark, 
  User, LogOut, Search, Settings,
  Sun, Moon, ChevronDown
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { authService } from '../../services/api';

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const { theme, toggleTheme, isDark } = useTheme();
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [savedCount, setSavedCount] = useState(0);
  const profileDropdownRef = useRef(null);

  useEffect(() => {
    if (isAuthenticated) {
      authService.getSavedEvents()
        .then((res) => setSavedCount(res.data?.length || 0))
        .catch(() => setSavedCount(0));
    } else {
      setSavedCount(0);
    }
  }, [isAuthenticated, location.pathname]);

  useEffect(() => {
    setProfileDropdownOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (profileDropdownRef.current && !profileDropdownRef.current.contains(e.target)) {
        setProfileDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  const primaryNav = [
    { name: 'Discover', path: '/', icon: Compass, exact: true },
    { name: 'States & UTs', path: '/india', icon: MapPin },
    { name: 'Global & Online', path: '/global', icon: Globe },
  ];

  const isActive = (link) => {
    if (link.exact) return location.pathname === link.path;
    return location.pathname.startsWith(link.path);
  };

  const handleFocusSearch = () => {
    if (location.pathname !== '/') {
      navigate('/');
    }
    setTimeout(() => {
      const el = document.querySelector('[data-search-input]');
      if (el) {
        el.focus();
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 150);
  };

  return (
    <header 
      className="sticky top-0 z-40 w-full border-b border-border-subtle bg-surface-200/95 backdrop-blur-md transition-colors"
    >
      <div className="max-w-[1280px] mx-auto px-3 sm:px-6">
        <div className="flex items-center h-14 justify-between gap-2 sm:gap-4">

          {/* ── Brand Logo & Title ── */}
          <Link to="/" className="flex items-center gap-2 shrink-0 group">
            <div 
              className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg flex items-center justify-center font-extrabold text-xs tracking-tight transition-transform duration-200 group-hover:scale-105"
              style={{
                backgroundColor: 'var(--color-primary)',
                color: 'var(--color-primary-text)'
              }}
            >
              EH
            </div>
            <div className="flex flex-col">
              <span className="text-sm sm:text-[15px] font-bold tracking-tight text-text-primary leading-tight">
                EventHorizon<span className="text-primary font-normal text-xs ml-0.5 sm:ml-1 font-mono">AI</span>
              </span>
              <span className="text-[10px] text-text-muted hidden sm:inline leading-none">
                Developer Event Discovery
              </span>
            </div>
          </Link>

          {/* ── Desktop Primary Navigation (Discover, States, Global) ── */}
          <nav className="hidden md:flex items-center gap-1.5 min-w-0">
            {primaryNav.map((link) => {
              const Icon = link.icon;
              const active = isActive(link);
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                    active 
                      ? 'bg-surface-300 text-primary border border-primary/30 shadow-xs' 
                      : 'text-text-secondary hover:text-text-primary hover:bg-surface-100'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* ── Right Actions: Search + Theme Toggle + Profile Dropdown ── */}
          <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
            {/* Quick search button - visible on sm and up to prevent crowding on small screens */}
            <button
              onClick={handleFocusSearch}
              className="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs bg-surface-100 border border-border-subtle text-text-muted hover:text-text-primary hover:border-border-strong transition-colors"
              title="Search events"
            >
              <Search className="w-3.5 h-3.5" />
              <span className="hidden lg:inline">Search</span>
              <kbd className="hidden lg:inline text-[10px] font-mono px-1 rounded bg-surface-300 text-text-muted border border-border-subtle">/</kbd>
            </button>

            {/* Dark / Light Theme Toggle */}
            <button
              onClick={toggleTheme}
              aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
              className="p-2 rounded-lg bg-surface-100 border border-border-subtle text-text-muted hover:text-text-primary hover:border-border-strong transition-colors"
              title={isDark ? "Switch to Light Mode (Ivory & Terracotta)" : "Switch to Dark Mode (Burgundy & Rose Gold)"}
            >
              {isDark ? (
                <Sun className="w-4 h-4 text-gold transition-transform duration-200 hover:rotate-45" />
              ) : (
                <Moon className="w-4 h-4 text-primary transition-transform duration-200 hover:-rotate-12" />
              )}
            </button>

            {/* Profile Dropdown for Secondary Options */}
            <div className="relative" ref={profileDropdownRef}>
              {isAuthenticated ? (
                <div>
                  <button
                    onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                    className="flex items-center gap-2 p-1 pl-2 pr-2.5 rounded-lg bg-surface-100 border border-border-subtle hover:border-border-strong transition-colors"
                    aria-expanded={profileDropdownOpen}
                  >
                    <div 
                      className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                      style={{ backgroundColor: 'var(--color-primary-subtle)', color: 'var(--color-primary)' }}
                    >
                      {user.email[0].toUpperCase()}
                    </div>
                    <span className="text-xs font-medium text-text-primary truncate max-w-[80px] hidden sm:inline">
                      {user.full_name || user.email.split('@')[0]}
                    </span>
                    <ChevronDown className={`w-3.5 h-3.5 text-text-muted transition-transform ${profileDropdownOpen ? 'rotate-180' : ''}`} />
                  </button>

                  {/* Dropdown Card */}
                  {profileDropdownOpen && (
                    <div 
                      className="absolute right-0 mt-2 w-56 rounded-xl shadow-xl py-1.5 border border-border-strong bg-surface-200 animate-fade-in z-50 text-xs"
                    >
                      <div className="px-3.5 py-2 border-b border-border-subtle">
                        <p className="font-semibold text-text-primary truncate">{user.full_name || 'Developer'}</p>
                        <p className="text-[11px] text-text-muted truncate">{user.email}</p>
                        <span className="inline-block mt-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-300 text-text-secondary uppercase">
                          {user.role}
                        </span>
                      </div>

                      <Link
                        to="/saved"
                        className="flex items-center justify-between px-3.5 py-2 text-text-secondary hover:text-text-primary hover:bg-surface-300 transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <Bookmark className="w-3.5 h-3.5 text-primary" />
                          <span>Saved Opportunities</span>
                        </div>
                        {savedCount > 0 && (
                          <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded-full bg-primary/20 text-primary">
                            {savedCount}
                          </span>
                        )}
                      </Link>

                      {isAdmin && (
                        <Link
                          to="/admin"
                          className="flex items-center gap-2 px-3.5 py-2 text-text-secondary hover:text-text-primary hover:bg-surface-300 transition-colors"
                        >
                          <Settings className="w-3.5 h-3.5 text-green" />
                          <span>Operations Console</span>
                        </Link>
                      )}

                      <div className="border-t border-border-subtle mt-1 pt-1">
                        <button
                          onClick={logout}
                          className="w-full text-left flex items-center gap-2 px-3.5 py-2 text-error hover:bg-surface-300 transition-colors"
                        >
                          <LogOut className="w-3.5 h-3.5" />
                          <span>Sign Out</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center gap-1.5 sm:gap-2">
                  <Link
                    to="/login"
                    className="px-2.5 sm:px-3 py-1.5 text-xs font-semibold rounded-lg text-text-secondary hover:text-text-primary hover:bg-surface-100 transition-colors"
                  >
                    Sign In
                  </Link>
                  <div className="hidden sm:block">
                    <Link
                      to="/register"
                      className="btn-primary text-xs py-1.5 px-3"
                    >
                      Join Free
                    </Link>
                  </div>
                </div>
              )}
            </div>

          </div>

        </div>
      </div>
    </header>
  );
}
