import React, { useState } from 'react';
import { Search, Flame, Sun, Snowflake, Play, Zap, Mail, Sheet, Trash2, ExternalLink, Download, FileText, X } from 'lucide-react';
import { CallAudioPlayer } from './CallAudioPlayer';

export function LeadTable({
  leads,
  loading,
  filterTemp,
  setFilterTemp,
  searchQuery,
  setSearchQuery,
  onDelete,
  onRelay,
}) {
  const [selectedLead, setSelectedLead] = useState(null);
  const [activeAudioLead, setActiveAudioLead] = useState(null);

  const getTempBadge = (temp) => {
    switch (temp) {
      case 'HOT':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <Flame className="w-3.5 h-3.5 text-rose-500 animate-pulse" />
            HOT
          </span>
        );
      case 'WARM':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Sun className="w-3.5 h-3.5 text-amber-500" />
            WARM
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Snowflake className="w-3.5 h-3.5 text-blue-400" />
            COLD
          </span>
        );
    }
  };

  const exportCSV = () => {
    if (!leads.length) return;
    const headers = ['ID', 'Name', 'Email', 'Phone', 'Company', 'Temperature', 'Summary', 'Budget', 'Timeframe', 'Created At'];
    const rows = leads.map(l => [
      l.id,
      `"${l.name || ''}"`,
      `"${l.email || ''}"`,
      `"${l.phone || ''}"`,
      `"${l.company || ''}"`,
      l.lead_temperature,
      `"${(l.summary || '').replace(/"/g, '""')}"`,
      `"${l.budget || ''}"`,
      `"${l.timeframe || ''}"`,
      l.created_at
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `VoiceLeads_CRM_Export_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="glass-panel rounded-2xl border border-slate-800 shadow-2xl overflow-hidden mb-12">
      
      {/* Header Bar: Title, Search & Filter Controls */}
      <div className="p-5 border-b border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4 bg-slate-900/50">
        <div>
          <h2 className="text-xl font-bold text-white font-outfit flex items-center gap-2">
            Synchronized CRM Lead Pipeline
            <span className="text-xs font-normal text-slate-400 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700">
              {leads.length} Records
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Real-time leads qualified by Vapi Voice AI and synced to GSheets & n8n</p>
        </div>

        {/* Search & Filter Inputs */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          
          {/* Temperature Filters */}
          <div className="flex items-center gap-1 p-1 rounded-xl bg-slate-950 border border-slate-800">
            {['', 'HOT', 'WARM', 'COLD'].map((t) => (
              <button
                key={t}
                onClick={() => setFilterTemp(t)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  filterTemp === t
                    ? 'bg-brand-500 text-white shadow-md shadow-brand-500/20'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {t === '' ? 'ALL' : t}
              </button>
            ))}
          </div>

          {/* Search Bar */}
          <div className="relative flex-1 md:w-56">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search leads..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500"
            />
          </div>

          {/* CSV Export */}
          <button
            onClick={exportCSV}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white transition-all"
            title="Export CSV"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* CRM Lead Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800/80 bg-slate-950/60 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              <th className="py-3.5 px-4">Prospect & Company</th>
              <th className="py-3.5 px-4">Score</th>
              <th className="py-3.5 px-4">Intent & Summary</th>
              <th className="py-3.5 px-4">Budget / Timeframe</th>
              <th className="py-3.5 px-4 text-center">Sync Status</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-xs">
            {loading ? (
              <tr>
                <td colSpan="6" className="py-12 text-center text-slate-400">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
                    <span>Synchronizing CRM leads...</span>
                  </div>
                </td>
              </tr>
            ) : leads.length === 0 ? (
              <tr>
                <td colSpan="6" className="py-12 text-center text-slate-400">
                  <p className="text-slate-300 font-medium mb-1">No leads found</p>
                  <p className="text-xs text-slate-500">Trigger a call simulation or make a WebRTC voice call above to generate qualified leads.</p>
                </td>
              </tr>
            ) : (
              leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-slate-900/60 transition-colors">
                  
                  {/* Prospect Info */}
                  <td className="py-4 px-4">
                    <div className="font-bold text-white text-sm font-outfit">{lead.name}</div>
                    <div className="text-slate-400 text-[11px] flex items-center gap-2 mt-0.5">
                      <span>{lead.company || 'Direct Prospect'}</span>
                      {lead.email && <span className="text-slate-500">• {lead.email}</span>}
                    </div>
                    {lead.phone && <div className="text-[10px] text-brand-400 font-mono mt-0.5">{lead.phone}</div>}
                  </td>

                  {/* Temperature */}
                  <td className="py-4 px-4">
                    {getTempBadge(lead.lead_temperature)}
                  </td>

                  {/* Intent & Summary */}
                  <td className="py-4 px-4 max-w-xs">
                    <div className="font-semibold text-slate-200 truncate">{lead.intent || 'Voice Qualification'}</div>
                    <p className="text-slate-400 text-[11px] line-clamp-2 mt-0.5 leading-relaxed">
                      {lead.summary || 'No summary generated.'}
                    </p>
                  </td>

                  {/* Budget & Timeframe */}
                  <td className="py-4 px-4 text-slate-300">
                    <div className="font-semibold text-emerald-400">{lead.budget || 'To be defined'}</div>
                    <div className="text-[11px] text-slate-400 mt-0.5">{lead.timeframe || 'Immediate'}</div>
                  </td>

                  {/* Sync Badges */}
                  <td className="py-4 px-4 text-center">
                    <div className="flex items-center justify-center gap-2">
                      {/* GSheets */}
                      <span
                        title={lead.synced_to_gsheets ? 'Synced to Google Sheets' : 'Local GSheets Backup'}
                        className={`p-1.5 rounded-lg border text-xs ${
                          lead.synced_to_gsheets
                            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                            : 'bg-slate-800 border-slate-700 text-slate-500'
                        }`}
                      >
                        <Sheet className="w-3.5 h-3.5" />
                      </span>

                      {/* n8n */}
                      <span
                        title={lead.synced_to_n8n ? 'Relayed to n8n Webhook' : 'n8n Relay Ready'}
                        className={`p-1.5 rounded-lg border text-xs ${
                          lead.synced_to_n8n
                            ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                            : 'bg-slate-800 border-slate-700 text-slate-500'
                        }`}
                      >
                        <Zap className="w-3.5 h-3.5" />
                      </span>

                      {/* Email */}
                      <span
                        title={lead.email_sent ? 'SMTP Notification Sent' : 'Email Alert Ready'}
                        className={`p-1.5 rounded-lg border text-xs ${
                          lead.email_sent
                            ? 'bg-brand-500/10 border-brand-500/30 text-brand-400'
                            : 'bg-slate-800 border-slate-700 text-slate-500'
                        }`}
                      >
                        <Mail className="w-3.5 h-3.5" />
                      </span>
                    </div>
                  </td>

                  {/* Actions */}
                  <td className="py-4 px-4 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      
                      {/* Audio Player Button */}
                      {lead.recording_url && (
                        <button
                          onClick={() => setActiveAudioLead(lead)}
                          className="p-2 rounded-lg bg-slate-800 hover:bg-brand-500/20 text-slate-300 hover:text-brand-400 transition-all border border-slate-700"
                          title="Listen Call Recording"
                        >
                          <Play className="w-3.5 h-3.5" />
                        </button>
                      )}

                      {/* View Details Modal */}
                      <button
                        onClick={() => setSelectedLead(lead)}
                        className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all border border-slate-700"
                        title="View Full Call Details & Transcript"
                      >
                        <FileText className="w-3.5 h-3.5" />
                      </button>

                      {/* Manual n8n Relay Trigger */}
                      <button
                        onClick={() => onRelay(lead)}
                        className="p-2 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/20 transition-all"
                        title="Trigger n8n Automation Relay"
                      >
                        <Zap className="w-3.5 h-3.5" />
                      </button>

                      {/* Delete */}
                      <button
                        onClick={() => onDelete(lead.id)}
                        className="p-2 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 transition-all"
                        title="Delete Lead Record"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>

                    </div>
                  </td>

                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Audio Player Modal / Popover */}
      {activeAudioLead && (
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between">
          <div className="flex-1 max-w-md">
            <CallAudioPlayer
              audioUrl={activeAudioLead.recording_url}
              leadName={`${activeAudioLead.name} - ${activeAudioLead.company || 'Call Recording'}`}
            />
          </div>
          <button
            onClick={() => setActiveAudioLead(null)}
            className="ml-4 p-2 text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* Full Lead Details Drawer Modal */}
      {selectedLead && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 max-h-[85vh] overflow-y-auto shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
              <div>
                <h3 className="text-xl font-bold text-white font-outfit">{selectedLead.name}</h3>
                <p className="text-xs text-slate-400">{selectedLead.company} • {selectedLead.created_at}</p>
              </div>
              <button
                onClick={() => setSelectedLead(null)}
                className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-4 bg-slate-950 p-4 rounded-xl border border-slate-800">
                <div>
                  <span className="text-slate-500 font-semibold block">Email:</span>
                  <span className="text-slate-200 font-medium">{selectedLead.email || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-semibold block">Phone:</span>
                  <span className="text-slate-200 font-medium">{selectedLead.phone || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-semibold block">Budget:</span>
                  <span className="text-emerald-400 font-bold">{selectedLead.budget || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-semibold block">Timeframe:</span>
                  <span className="text-slate-200 font-medium">{selectedLead.timeframe || 'N/A'}</span>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-brand-400 mb-1">AI Generated Summary</h4>
                <p className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 leading-relaxed">
                  {selectedLead.summary}
                </p>
              </div>

              {selectedLead.transcript && (
                <div>
                  <h4 className="font-bold text-purple-400 mb-1">Full Call Transcript</h4>
                  <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 font-sans whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                    {selectedLead.transcript}
                  </pre>
                </div>
              )}
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setSelectedLead(null)}
                className="px-5 py-2 rounded-xl bg-brand-500 hover:bg-brand-400 text-white font-semibold text-xs"
              >
                Close Details
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
