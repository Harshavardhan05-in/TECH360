import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import MobileBottomNav from './components/layout/MobileBottomNav';
import FloatingAssistant from './components/assistant/FloatingAssistant';
import ViewLimitModal from './components/feedback/ViewLimitModal';

import HomePage from './pages/HomePage';
import EventDetailPage from './pages/EventDetailPage';
import IndiaExplorerPage from './pages/IndiaExplorerPage';
import GlobalEventsPage from './pages/GlobalEventsPage';
import AssistantPage from './pages/AssistantPage';
import SavedEventsPage from './pages/SavedEventsPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <div className="min-h-screen flex flex-col bg-background text-text-primary pb-14 md:pb-0 transition-colors">
            {/* Desktop & Mobile Header */}
            <Navbar />
            
            {/* Main Page Content */}
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/events/:slug" element={<EventDetailPage />} />
                <Route path="/india" element={<IndiaExplorerPage />} />
                <Route path="/india/:stateSlug" element={<IndiaExplorerPage />} />
                <Route path="/global" element={<GlobalEventsPage />} />
                <Route path="/assistant" element={<AssistantPage />} />
                <Route path="/saved" element={<SavedEventsPage />} />
                <Route path="/admin" element={<AdminDashboardPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>

            {/* Universal Floating AI Assistant Widget */}
            <FloatingAssistant />

            {/* Persistent Mobile Bottom Navigation */}
            <MobileBottomNav />

            {/* Footer */}
            <Footer />

            {/* Anonymous View Limit Modal */}
            <ViewLimitModal />
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}
