import React from 'react';
import { Navbar } from './components/Navbar';
import { StatsOverview } from './components/StatsOverview';
import { VoiceCallButton } from './components/VoiceCallButton';
import { LeadTable } from './components/LeadTable';
import { useVapi } from './hooks/useVapi';
import { useLeads } from './hooks/useLeads';
import { Sparkles, Layers, ShieldCheck, ArrowUpRight } from 'lucide-react';

export default function App() {
  const vapi = useVapi();
  const leadsHook = useLeads();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      
      {/* Top Navbar Header */}
      <Navbar
        onSimulateCall={leadsHook.simulateCall}
        isSimulation={vapi.isSimulation}
        backendOnline={!leadsHook.error}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-8">
        
        {/* Banner Announcement */}
        <div className="mb-6 p-4 rounded-2xl bg-gradient-to-r from-brand-500/10 via-purple-500/10 to-indigo-500/10 border border-brand-500/20 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-brand-500/20 text-brand-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white font-outfit">VocalSync Automated Lead Processing Active</h3>
              <p className="text-xs text-slate-400">Calls are evaluated using AI, pushed to Google Sheets, and dispatched via n8n & SMTP Email.</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-3.5 h-3.5" />
              WebRTC Encrypted
            </span>
          </div>
        </div>

        {/* WebRTC Voice Agent Caller */}
        <VoiceCallButton
          isCalling={vapi.isCalling}
          isMuted={vapi.isMuted}
          callStatus={vapi.callStatus}
          transcripts={vapi.transcripts}
          volumeLevel={vapi.volumeLevel}
          callDuration={vapi.callDuration}
          isSimulation={vapi.isSimulation}
          onStartCall={vapi.startCall}
          onStopCall={vapi.stopCall}
          onToggleMute={vapi.toggleMute}
        />

        {/* Analytics Overview Cards */}
        <StatsOverview
          stats={leadsHook.stats}
          activeFilter={leadsHook.filterTemp}
          onFilterChange={leadsHook.setFilterTemp}
        />

        {/* CRM Synchronized Lead Table */}
        <LeadTable
          leads={leadsHook.leads}
          loading={leadsHook.loading}
          filterTemp={leadsHook.filterTemp}
          setFilterTemp={leadsHook.setFilterTemp}
          searchQuery={leadsHook.searchQuery}
          setSearchQuery={leadsHook.setSearchQuery}
          onDelete={leadsHook.deleteLead}
          onRelay={leadsHook.relayLead}
        />

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span className="font-bold text-slate-400">VoiceLeads AI</span> • VocalSync CRM & Automation Microservice
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-brand-400 flex items-center gap-1">
              FastAPI Swagger Docs <ArrowUpRight className="w-3 h-3" />
            </a>
          </div>
        </div>
      </footer>

    </div>
  );
}
