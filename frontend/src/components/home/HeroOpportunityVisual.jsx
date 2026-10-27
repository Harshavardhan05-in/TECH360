import React from 'react';
import { Code, Trophy, Users, Sparkles, MapPin, CheckCircle2 } from 'lucide-react';

export default function HeroOpportunityVisual() {
  return (
    <div className="relative w-full max-w-[380px] sm:max-w-[420px] mx-auto flex items-center justify-center p-2 select-none">
      {/* Background radial glow */}
      <div 
        className="absolute inset-0 rounded-full blur-3xl opacity-20 pointer-events-none"
        style={{
          background: 'radial-gradient(circle, var(--color-primary) 0%, transparent 70%)'
        }}
      />

      {/* SVG Canvas for Connected Developer Grid */}
      <svg
        viewBox="0 0 400 320"
        className="w-full h-auto overflow-visible relative z-10"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <defs>
          {/* Subtle pulse animation for opportunity signals */}
          <style>{`
            @keyframes signalPulse {
              0% { r: 18; opacity: 0.8; }
              50% { r: 36; opacity: 0.2; }
              100% { r: 54; opacity: 0; }
            }
            @keyframes nodeFloat1 {
              0%, 100% { transform: translateY(0px); }
              50% { transform: translateY(-4px); }
            }
            @keyframes nodeFloat2 {
              0%, 100% { transform: translateY(0px); }
              50% { transform: translateY(4px); }
            }
            @keyframes beamFlow {
              0% { stroke-dashoffset: 40; }
              100% { stroke-dashoffset: 0; }
            }
            .anim-pulse-ring {
              animation: signalPulse 3.5s cubic-bezier(0.2, 0.8, 0.2, 1) infinite;
              transform-origin: 200px 160px;
            }
            .anim-float-1 {
              animation: nodeFloat1 4s ease-in-out infinite;
            }
            .anim-float-2 {
              animation: nodeFloat2 4.5s ease-in-out infinite;
            }
            .anim-beam {
              stroke-dasharray: 6 6;
              animation: beamFlow 8s linear infinite;
            }
            @media (prefers-reduced-motion: reduce) {
              .anim-pulse-ring, .anim-float-1, .anim-float-2, .anim-beam {
                animation: none !important;
              }
            }
          `}</style>
        </defs>

        {/* ── Background Connection Network ── */}
        {/* Soft connecting grid lines representing developer discovery network */}
        <path
          d="M 60 90 L 200 160 L 340 80 M 80 240 L 200 160 L 320 230 M 200 60 L 200 160"
          className="stroke-border-subtle"
          strokeWidth="1.5"
          strokeOpacity="0.8"
        />
        <path
          d="M 60 90 L 80 240 M 340 80 L 320 230"
          className="stroke-border-subtle"
          strokeWidth="1"
          strokeDasharray="4 4"
          strokeOpacity="0.5"
        />

        {/* Animated active discovery data beams linking to central opportunity hub */}
        <line
          x1="60" y1="90" x2="200" y2="160"
          className="stroke-primary anim-beam"
          strokeWidth="2"
          strokeOpacity="0.6"
        />
        <line
          x1="340" y1="80" x2="200" y2="160"
          className="stroke-green anim-beam"
          strokeWidth="2"
          strokeOpacity="0.6"
        />
        <line
          x1="80" y1="240" x2="200" y2="160"
          className="stroke-gold anim-beam"
          strokeWidth="2"
          strokeOpacity="0.6"
        />
        <line
          x1="320" y1="230" x2="200" y2="160"
          className="stroke-rose anim-beam"
          strokeWidth="2"
          strokeOpacity="0.6"
        />

        {/* ── Central Hub Signal Waves (Radar finding opportunities) ── */}
        <circle
          cx="200"
          cy="160"
          r="24"
          className="anim-pulse-ring stroke-primary"
          strokeWidth="1.5"
          fill="none"
        />
        <circle
          cx="200"
          cy="160"
          r="48"
          className="stroke-border-strong"
          strokeWidth="1"
          strokeDasharray="4 4"
          fill="none"
          opacity="0.4"
        />

        {/* ── Opportunity Node 1 (Top Left): Hackathon Buildathon ── */}
        <g className="anim-float-1" transform="translate(40, 65)">
          <rect
            width="110"
            height="38"
            rx="10"
            className="fill-surface-200 stroke-border-subtle shadow-sm"
            strokeWidth="1.5"
          />
          <circle cx="18" cy="19" r="10" className="fill-primary" fillOpacity="0.15" />
          <circle cx="18" cy="19" r="4" className="fill-primary" />
          <text x="34" y="17" className="fill-text-primary text-[10px] font-sans font-bold">
            Hackathons
          </text>
          <text x="34" y="28" className="fill-text-muted text-[8.5px] font-mono">
            Active Challenges
          </text>
        </g>

        {/* ── Opportunity Node 2 (Top Right): Developer Communities ── */}
        <g className="anim-float-2" transform="translate(250, 55)">
          <rect
            width="115"
            height="38"
            rx="10"
            className="fill-surface-200 stroke-border-subtle shadow-sm"
            strokeWidth="1.5"
          />
          <circle cx="18" cy="19" r="10" className="fill-green" fillOpacity="0.15" />
          <circle cx="18" cy="19" r="4" className="fill-green" />
          <text x="34" y="17" className="fill-text-primary text-[10px] font-sans font-bold">
            Conferences
          </text>
          <text x="34" y="28" className="fill-text-muted text-[8.5px] font-mono">
            Keynotes & Summits
          </text>
        </g>

        {/* ── Opportunity Node 3 (Bottom Left): Hands-on Workshops ── */}
        <g className="anim-float-2" transform="translate(50, 215)">
          <rect
            width="105"
            height="38"
            rx="10"
            className="fill-surface-200 stroke-border-subtle shadow-sm"
            strokeWidth="1.5"
          />
          <circle cx="18" cy="19" r="10" className="fill-gold" fillOpacity="0.15" />
          <circle cx="18" cy="19" r="4" className="fill-gold" />
          <text x="34" y="17" className="fill-text-primary text-[10px] font-sans font-bold">
            Workshops
          </text>
          <text x="34" y="28" className="fill-text-muted text-[8.5px] font-mono">
            Hands-on Learning
          </text>
        </g>

        {/* ── Opportunity Node 4 (Bottom Right): Verified Reachability ── */}
        <g className="anim-float-1" transform="translate(245, 205)">
          <rect
            width="115"
            height="38"
            rx="10"
            className="fill-surface-200 stroke-border-subtle shadow-sm"
            strokeWidth="1.5"
          />
          <circle cx="18" cy="19" r="10" className="fill-rose" fillOpacity="0.15" />
          <circle cx="18" cy="19" r="4" className="fill-rose" />
          <text x="34" y="17" className="fill-text-primary text-[10px] font-sans font-bold">
            Verified Portals
          </text>
          <text x="34" y="28" className="fill-text-muted text-[8.5px] font-mono">
            Direct Registration
          </text>
        </g>

        {/* ── Central Hub: Code & Opportunity Beacon ── */}
        <g transform="translate(160, 120)">
          {/* Card Surface */}
          <rect
            width="80"
            height="80"
            rx="20"
            className="fill-surface-200 stroke-primary shadow-xl"
            strokeWidth="2"
          />
          {/* Internal badge accent */}
          <rect
            x="8"
            y="8"
            width="64"
            height="64"
            rx="14"
            className="fill-surface-100"
          />
          
          {/* Code Brackets Illustration */}
          <path
            d="M 33 34 L 25 40 L 33 46 M 47 34 L 55 40 L 47 46 M 42 32 L 38 48"
            className="stroke-primary"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          
          {/* Status signal dot */}
          <circle cx="40" cy="60" r="3" className="fill-green" />
          <circle cx="40" cy="60" r="6" className="stroke-green" strokeWidth="1" opacity="0.4" />
        </g>
      </svg>
    </div>
  );
}
