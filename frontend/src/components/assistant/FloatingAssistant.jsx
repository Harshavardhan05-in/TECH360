import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { 
  Sparkles, MessageSquare, X, Send, Bot, User, 
  ExternalLink, Calendar, MapPin, ShieldCheck, 
  RefreshCw, ChevronDown, Check, ArrowRight
} from 'lucide-react';
import { assistantService } from '../../services/api';
import { useTheme } from '../../context/ThemeContext';
import { getRegistrationAction, getInternalEventRoute, getSafeUrl } from '../../utils/navigation';

export default function FloatingAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! How can I help you discover events today?",
      events: [],
      suggested_followups: [
        "Find AI hackathons in Telangana",
        "Show upcoming online workshops",
        "What can you do?",
        "Are there any free hackathons?"
      ]
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [hasUnread, setHasUnread] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const { isDark } = useTheme();

  // Scroll to bottom when messages update
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen, loading]);

  // Focus input on open
  useEffect(() => {
    if (isOpen) {
      setHasUnread(false);
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen]);

  const handleSend = async (userText) => {
    const textToSend = userText || query;
    if (!textToSend.trim() || loading) return;

    const trimmed = textToSend.trim();
    const updatedMessages = [...messages, { role: 'user', content: trimmed }];
    setMessages(updatedMessages);
    setQuery('');
    setLoading(true);

    try {
      // Build prior conversation context (last 6 turns, omitting events for compact payload)
      const contextMessages = updatedMessages.slice(-6).map(m => ({
        role: m.role,
        content: m.content
      }));

      const res = await assistantService.query({
        query: trimmed,
        messages: contextMessages
      });

      setMessages([
        ...updatedMessages,
        {
          role: 'assistant',
          content: res.data.answer,
          events: res.data.events || [],
          suggested_followups: res.data.suggested_followups || [],
          disclaimer: res.data.disclaimer
        }
      ]);

      if (!isOpen) {
        setHasUnread(true);
      }
    } catch (err) {
      setMessages([
        ...updatedMessages,
        {
          role: 'assistant',
          content: "I'm having trouble connecting to the event retrieval service right now. Please try again in a moment.",
          events: [],
          suggested_followups: ["Find AI hackathons in Telangana", "Show upcoming online workshops"]
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleResetChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: "Hi! How can I help you discover events today?",
        events: [],
        suggested_followups: [
          "Find AI hackathons in Telangana",
          "Show upcoming online workshops",
          "What can you do?",
          "Are there any free hackathons?"
        ]
      }
    ]);
  };

  return (
    <>
      {/* Floating Trigger Button - Positioned above persistent MobileBottomNav on mobile */}
      <div className="fixed bottom-20 right-4 md:bottom-6 md:right-6 z-40">
        {!isOpen && (
          <button
            onClick={() => setIsOpen(true)}
            aria-label="Open EventHorizon AI Assistant"
            className="group relative flex items-center gap-2 px-4 py-2.5 rounded-full shadow-xl transition-all duration-200 hover:scale-105 active:scale-95 bg-primary text-background font-bold text-xs tracking-wide"
          >
            <Sparkles className="w-4 h-4 fill-current" />
            <span>Ask AI</span>
            {hasUnread && (
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-coral animate-ping" />
            )}
          </button>
        )}
      </div>

      {/* Floating Chat Modal / Drawer - Positioned above MobileBottomNav with safe viewport margins */}
      {isOpen && (
        <div 
          className="fixed bottom-20 right-2 sm:right-4 md:bottom-6 md:right-6 z-50 w-[calc(100vw-1rem)] sm:w-[410px] h-[520px] max-h-[calc(100vh-6.5rem)] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-fade-in border border-border-strong"
          style={{
            backgroundColor: 'var(--color-surface-200)',
            boxShadow: '0 16px 48px rgba(0, 0, 0, 0.45)'
          }}
        >
          {/* Header */}
          <div 
            className="px-4 py-3 border-b border-border-subtle flex items-center justify-between shrink-0 bg-surface-100"
          >
            <div className="flex items-center gap-2.5 min-w-0">
              <div 
                className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 bg-primary text-background"
              >
                <Sparkles className="w-4 h-4 fill-current" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-1.5">
                  <h3 className="text-xs font-bold truncate text-text-primary">
                    EventHorizon Assistant
                  </h3>
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full badge-verified">
                    Verified
                  </span>
                </div>
                <p className="text-[10px] text-text-muted truncate">
                  Tech Discovery · India & Worldwide
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={handleResetChat}
                title="Clear conversation"
                className="p-1.5 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-300 transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                title="Minimize assistant"
                className="p-1.5 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-300 transition-colors"
              >
                <ChevronDown className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                title="Close assistant"
                className="p-1.5 rounded-lg text-text-muted hover:text-coral hover:bg-surface-300 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages Scroll Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.role === 'assistant' && (
                  <div 
                    className="w-6 h-6 rounded-md flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold"
                    style={{ backgroundColor: 'var(--color-primary-subtle)', color: 'var(--color-primary)' }}
                  >
                    AI
                  </div>
                )}

                <div 
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed ${
                    m.role === 'user' 
                      ? 'rounded-br-sm' 
                      : 'rounded-bl-sm border border-border-subtle bg-surface-100'
                  }`}
                  style={m.role === 'user' ? {
                    backgroundColor: 'var(--color-primary)',
                    color: 'var(--color-primary-text)',
                    fontWeight: 500,
                  } : {
                    color: 'var(--color-text-primary)',
                  }}
                >
                  <div className="prose prose-xs dark:prose-invert max-w-none">
                    <ReactMarkdown>{m.content}</ReactMarkdown>
                  </div>

                  {/* Render cited event cards if present */}
                  {m.events && m.events.length > 0 && (
                    <div className="mt-3 space-y-2 pt-2 border-t border-border-subtle">
                      {m.events.map((ev) => (
                        <div 
                          key={ev.id}
                          className="p-2.5 rounded-xl bg-surface-200 border border-border-subtle hover:border-border-strong transition-all space-y-1.5"
                        >
                          <div className="flex items-start justify-between gap-1.5">
                            <Link 
                              to={getInternalEventRoute(ev)}
                              onClick={() => setIsOpen(false)}
                              className="font-semibold text-xs text-primary hover:underline line-clamp-1"
                            >
                              {ev.title}
                            </Link>
                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded badge-verified shrink-0">
                              {ev.category}
                            </span>
                          </div>

                          <div className="flex items-center gap-2 text-[10px] text-text-muted flex-wrap">
                            <span className="flex items-center gap-1">
                              <Calendar className="w-3 h-3 text-mint" />
                              <span>{ev.start_date}</span>
                            </span>
                            <span>·</span>
                            <span className="flex items-center gap-1">
                              <MapPin className="w-3 h-3 text-mint" />
                              <span className="truncate max-w-[120px]">{ev.city || ev.state || ev.format}</span>
                            </span>
                            {ev.is_free && (
                              <>
                                <span>·</span>
                                <span className="text-mint font-medium">Free</span>
                              </>
                            )}
                          </div>

                          <div className="flex items-center justify-between pt-1">
                            <Link
                              to={getInternalEventRoute(ev)}
                              onClick={() => setIsOpen(false)}
                              className="text-[11px] font-semibold text-text-secondary hover:text-text-primary inline-flex items-center gap-1"
                            >
                              <span>Details</span>
                              <ArrowRight className="w-3 h-3" />
                            </Link>
                            
                            {(() => {
                              const action = getRegistrationAction(ev);
                              if (action.type === 'external') {
                                return (
                                  <a
                                    href={action.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="btn-primary text-[10px] py-0.5 px-2 flex items-center gap-1 font-semibold"
                                  >
                                    <span>Register</span>
                                    <ExternalLink className="w-2.5 h-2.5" />
                                  </a>
                                );
                              }
                              return (
                                <Link
                                  to={getInternalEventRoute(ev)}
                                  onClick={() => setIsOpen(false)}
                                  className="text-[10px] font-semibold text-primary hover:underline"
                                >
                                  <span>View Details</span>
                                </Link>
                              );
                            })()}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Render Suggested Followups if available */}
                  {m.role === 'assistant' && m.suggested_followups && m.suggested_followups.length > 0 && idx === messages.length - 1 && (
                    <div className="mt-3 pt-2 border-t border-border-subtle space-y-1.5">
                      <span className="text-[10px] font-mono uppercase text-text-muted">Suggested:</span>
                      <div className="flex flex-wrap gap-1.5">
                        {m.suggested_followups.map((sug, sIdx) => (
                          <button
                            key={sIdx}
                            onClick={() => handleSend(sug)}
                            disabled={loading}
                            className="text-[11px] px-2 py-1 rounded-lg bg-surface-200 border border-border-subtle hover:border-primary text-text-secondary hover:text-text-primary text-left transition-colors"
                          >
                            {sug}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {loading && (
              <div className="flex gap-2.5 justify-start">
                <div 
                  className="w-6 h-6 rounded-md flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold"
                  style={{ backgroundColor: 'var(--color-primary-subtle)', color: 'var(--color-primary)' }}
                >
                  AI
                </div>
                <div className="rounded-2xl rounded-bl-sm px-3.5 py-3 border border-border-subtle bg-surface-100 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 rounded-full bg-mint animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 rounded-full bg-coral animate-bounce" style={{ animationDelay: '300ms' }} />
                  <span className="text-[11px] text-text-muted ml-1.5">Checking ground-truth database...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Footer Input Area */}
          <div className="p-3 border-t border-border-subtle bg-surface-100 shrink-0">
            <div className="flex items-center gap-2">
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about hackathons, workshops, conferences..."
                disabled={loading}
                className="flex-1 px-3.5 py-2 rounded-xl text-xs bg-surface-200 border border-border-subtle text-text-primary placeholder:text-text-muted outline-none focus:border-primary transition-colors"
              />
              <button
                onClick={() => handleSend()}
                disabled={!query.trim() || loading}
                aria-label="Send message"
                className="p-2 rounded-xl btn-primary text-xs shrink-0 disabled:opacity-40"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="flex items-center justify-between px-1 mt-1.5 text-[10px] text-text-muted">
              <span>Press Enter to send</span>
              <span>Zero-hallucination verified catalog</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
