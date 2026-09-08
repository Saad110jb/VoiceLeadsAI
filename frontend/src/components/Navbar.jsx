import React, { useState, useEffect } from 'react';
import { Mic, Radio, Zap, CheckCircle2, ShieldCheck, RefreshCw } from 'lucide-react';

export function Navbar({ onSimulateCall, isSimulation, backendOnline = true }) {
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="sticky top-0 z-40 border-b border-slate-800/80 glass-panel bg-slate-950/80 backdrop-blur-md px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand Logo & Name */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-500 via-brand-accent to-indigo-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Mic className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white font-outfit">VoiceLeads AI</h1>
              <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/20">
                VocalSync CRM v1.0
              </span>
            </div>
            <p className="text-xs text-slate-400">Autonomous WebRTC Voice Agent & Multi-Channel CRM Sync</p>
          </div>
        </div>

        {/* System Connectivity Indicators */}
        <div className="hidden md:flex items-center gap-6 text-xs">
          
          {/* FastAPI Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800">
            <span className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
            <span className="text-slate-300 font-medium">FastAPI Engine</span>
            <span className="text-slate-500">Port 8000</span>
          </div>

          {/* Vapi WebRTC Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800">
            <Radio className="w-3.5 h-3.5 text-brand-400 animate-pulse" />
            <span className="text-slate-300 font-medium">Vapi WebRTC</span>
            <span className="text-emerald-400 text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-emerald-500/10">Active</span>
          </div>

          {/* n8n Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-300 font-medium">n8n Relay</span>
            <span className="text-slate-500">Webhooks Ready</span>
          </div>

          {/* Clock */}
          <div className="text-slate-400 font-mono font-medium text-xs px-2 py-1">
            {currentTime}
          </div>
        </div>

        {/* Action Button: Simulation Trigger */}
        <div className="flex items-center gap-3">
          <button
            onClick={onSimulateCall}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-white bg-slate-800 hover:bg-slate-700 active:scale-95 transition-all rounded-lg border border-slate-700 shadow-sm"
            title="Simulate an incoming Vapi voice call to test AI extraction and CRM workflow"
          >
            <RefreshCw className="w-3.5 h-3.5 text-brand-400" />
            <span>Simulate Inbound Call</span>
          </button>
        </div>

      </div>
    </header>
  );
}
