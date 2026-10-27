import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { 
  Sparkles, Send, ShieldCheck, 
  ArrowRight, ExternalLink, RefreshCw, 
  Calendar, MapPin, Award
} from 'lucide-react';
import { assistantService } from '../services/api';
import { getRegistrationAction, getInternalEventRoute, getSafeUrl } from '../utils/navigation';

export default function AssistantPage() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! How can I help you discover events today? I can help you find verified hackathons, developer conferences, and technical workshops across India's 28 states & 8 Union Territories or global online events.",
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
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (userText) => {
    const textToSend = userText || query;
    if (!textToSend.trim() || loading) return;

    const trimmed = textToSend.trim();
    const updatedMessages = [...messages, { role: 'user', content: trimmed }];
    setMessages(updatedMessages);
    setQuery('');
    setLoading(true);

    try {
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
    } catch (err) {
      setMessages([
        ...updatedMessages,
        {
          role: 'assistant',
          content: "I encountered a communication error while querying the event database. Please try again.",
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
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
      {/* Header */}
      <div 
        className="eh-card p-6 sm:p-8 space-y-3 relative overflow-hidden"
        style={{
          background: 'linear-gradient(135deg, rgba(168, 138, 255, 0.14) 0%, rgba(131, 229, 197, 0.1) 100%)',
        }}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1.5">
            <div className="inline-flex items-center gap-1.5 text-xs font-mono badge-verified px-2.5 py-0.5 rounded-md">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Zero-Hallucination Grounded Engine</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-text-primary tracking-tight">
              AI Event Discovery Assistant
            </h1>
            <p className="text-xs sm:text-sm text-text-secondary">
              Conversational assistant grounded in verified technical event records across India and worldwide.
            </p>
          </div>

          <button
            onClick={handleResetChat}
            title="Clear Chat"
            className="p-2 rounded-xl btn-secondary text-xs flex items-center gap-1.5 shrink-0"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">New Chat</span>
          </button>
        </div>
      </div>

      {/* Suggested Starter Prompts */}
      <div className="space-y-2">
        <span className="text-[11px] font-mono uppercase text-text-muted">Suggested prompts:</span>
        <div className="flex flex-wrap gap-2">
          {[
            "Find AI hackathons in Telangana",
            "Show upcoming online workshops",
            "What can you do?",
            "Are there any free hackathons with prizes?",
            "What events are happening in Karnataka?"
          ].map((p, i) => (
            <button
              key={i}
              onClick={() => handleSend(p)}
              disabled={loading}
              className="text-xs text-text-secondary bg-surface-200 hover:bg-surface-300 border border-border-subtle hover:border-primary px-3 py-1.5 rounded-xl transition-colors text-left"
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Messages Stream */}
      <div className="eh-card p-4 sm:p-6 space-y-6 min-h-[460px]">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {m.role === 'assistant' && (
              <div 
                className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold"
                style={{ backgroundColor: 'var(--color-primary-subtle)', color: 'var(--color-primary)' }}
              >
                AI
              </div>
            )}

            <div 
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs sm:text-sm leading-relaxed ${
                m.role === 'user' 
                  ? 'rounded-br-sm' 
                  : 'rounded-bl-sm border border-border-subtle bg-surface-100'
              }`}
              style={m.role === 'user' ? {
                backgroundColor: 'var(--color-primary)',
                color: '#11101A',
                fontWeight: 500,
              } : {
                color: 'var(--color-text-primary)',
              }}
            >
              <div className="prose prose-xs sm:prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown>{m.content}</ReactMarkdown>
              </div>

              {/* Render citations if present */}
              {m.events && m.events.length > 0 && (
                <div className="mt-4 space-y-2.5 pt-3 border-t border-border-subtle">
                  {m.events.map((ev) => (
                    <div 
                      key={ev.id}
                      className="p-3 rounded-xl bg-surface-200 border border-border-subtle hover:border-border-strong transition-all space-y-1.5"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <Link 
                          to={`/events/${ev.slug}`}
                          className="font-bold text-xs sm:text-sm text-primary hover:underline line-clamp-1"
                        >
                          {ev.title}
                        </Link>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded badge-verified shrink-0">
                          {ev.category}
                        </span>
                      </div>

                      <div className="flex items-center gap-3 text-[11px] text-text-muted flex-wrap">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3 text-mint" />
                          <span>{ev.start_date}</span>
                        </span>
                        <span>·</span>
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-coral" />
                          <span>{ev.city || ev.state || ev.format}</span>
                        </span>
                        {ev.is_free && (
                          <>
                            <span>·</span>
                            <span className="text-mint font-semibold">Free Entry</span>
                          </>
                        )}
                      </div>

                      <div className="flex items-center justify-between pt-1">
                        <Link
                          to={getInternalEventRoute(ev)}
                          className="text-xs font-semibold text-text-secondary hover:text-text-primary inline-flex items-center gap-1"
                        >
                          <span>Full Details</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Link>
                        
                        {(() => {
                          const action = getRegistrationAction(ev);
                          if (action.type === 'external') {
                            return (
                              <a
                                href={action.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn-primary text-xs py-1 px-3 flex items-center gap-1 font-semibold"
                              >
                                <span>Register Now</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            );
                          }
                          return (
                            <Link
                              to={getInternalEventRoute(ev)}
                              className="text-xs font-semibold text-primary hover:underline"
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

              {/* Suggested Followups */}
              {m.role === 'assistant' && m.suggested_followups && m.suggested_followups.length > 0 && idx === messages.length - 1 && (
                <div className="mt-4 pt-3 border-t border-border-subtle space-y-1.5">
                  <span className="text-[10px] font-mono uppercase text-text-muted">Suggested Next Steps:</span>
                  <div className="flex flex-wrap gap-2">
                    {m.suggested_followups.map((sug, sIdx) => (
                      <button
                        key={sIdx}
                        onClick={() => handleSend(sug)}
                        disabled={loading}
                        className="text-xs px-2.5 py-1.5 rounded-lg bg-surface-200 border border-border-subtle hover:border-primary text-text-secondary hover:text-text-primary text-left transition-colors"
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

        {loading && (
          <div className="flex gap-3 justify-start">
            <div 
              className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold"
              style={{ backgroundColor: 'var(--color-primary-subtle)', color: 'var(--color-primary)' }}
            >
              AI
            </div>
            <div className="rounded-2xl rounded-bl-sm px-4 py-3 border border-border-subtle bg-surface-100 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 rounded-full bg-mint animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 rounded-full bg-coral animate-bounce" style={{ animationDelay: '300ms' }} />
              <span className="text-xs text-text-muted ml-2">Retrieving authentic records from database...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="eh-card p-3 sm:p-4">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about hackathons, workshops, conferences, or states..."
            disabled={loading}
            className="flex-1 px-4 py-3 rounded-xl text-xs sm:text-sm bg-surface-100 border border-border-subtle text-text-primary placeholder:text-text-muted outline-none focus:border-primary transition-colors"
          />
          <button
            onClick={() => handleSend()}
            disabled={!query.trim() || loading}
            aria-label="Send message"
            className="p-3 rounded-xl btn-primary text-xs shrink-0 disabled:opacity-40"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="flex items-center justify-between px-1 mt-2 text-[11px] text-text-muted">
          <span>Press Enter to send, Shift+Enter for new line</span>
          <span>Zero-hallucination ground-truth retrieval</span>
        </div>
      </div>
    </div>
  );
}
