import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Compass, MapPin, Globe, Bookmark, Sun, Moon } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { authService } from '../../services/api';

export default function MobileBottomNav() {
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  const { toggleTheme, isDark } = useTheme();
  const [savedCount, setSavedCount] = useState(0);

  useEffect(() => {
    if (isAuthenticated) {
      authService.getSavedEvents()
        .then((res) => setSavedCount(res.data?.length || 0))
        .catch(() => setSavedCount(0));
    } else {
      setSavedCount(0);
    }
  }, [isAuthenticated, location.pathname]);

  const navItems = [
    { label: 'Discover', path: '/', icon: Compass, exact: true },
    { label: 'States', path: '/india', icon: MapPin },
    { label: 'Global', path: '/global', icon: Globe },
    { label: 'Saved', path: '/saved', icon: Bookmark, badge: savedCount },
  ];

  const isActive = (item) => {
    if (item.exact) return location.pathname === item.path;
    return location.pathname.startsWith(item.path);
  };

  return (
    <nav 
      aria-label="Mobile Navigation"
      className="md:hidden fixed bottom-0 left-0 right-0 z-30 border-t border-border-subtle bg-surface-200/95 backdrop-blur-md"
      style={{
        boxShadow: '0 -4px 16px rgba(0, 0, 0, 0.08)'
      }}
    >
      <div className="flex items-center justify-around h-14 px-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item);
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`relative flex flex-col items-center justify-center flex-1 py-1 transition-colors ${
                active ? 'text-primary' : 'text-text-muted hover:text-text-primary'
              }`}
            >
              <div className="relative">
                <Icon className={`w-4 h-4 ${active ? 'stroke-[2.5]' : ''}`} />
                {Boolean(item.badge && item.badge > 0) && (
                  <span 
                    className="absolute -top-1 -right-2 text-[9px] font-mono px-1 rounded-full font-bold bg-primary text-background"
                  >
                    {item.badge}
                  </span>
                )}
              </div>
              <span className={`text-[10px] mt-0.5 ${active ? 'font-semibold' : 'font-normal'}`}>
                {item.label}
              </span>
              {active && (
                <span 
                  className="absolute bottom-0 w-8 h-0.5 rounded-full bg-primary"
                />
              )}
            </Link>
          );
        })}

        {/* Theme Toggle Pill for Mobile */}
        <button
          onClick={toggleTheme}
          aria-label="Toggle light and dark mode"
          className="flex flex-col items-center justify-center flex-1 py-1 text-text-muted hover:text-text-primary transition-colors"
        >
          {isDark ? <Sun className="w-4 h-4 text-gold" /> : <Moon className="w-4 h-4 text-primary" />}
          <span className="text-[10px] mt-0.5">{isDark ? 'Light' : 'Dark'}</span>
        </button>
      </div>
    </nav>
  );
}
