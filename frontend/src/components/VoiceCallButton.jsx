import React, { useState } from 'react';
import { Phone, PhoneOff, Mic, MicOff, Volume2, Sparkles, Activity, MessageSquare, PhoneCall, Send } from 'lucide-react';
import { triggerOutboundCall } from '../services/api';

export function VoiceCallButton({
  isCalling,
  isMuted,
  callStatus,
  transcripts,
  volumeLevel,
  callDuration,
  isSimulation,
  onStartCall,
  onStopCall,
  onToggleMute,
}) {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [outboundStatus, setOutboundStatus] = useState(null);
  const [isDialing, setIsDialing] = useState(false);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleOutboundPhoneCall = async (e) => {
    e.preventDefault();
    if (!phoneNumber) return;
    setIsDialing(true);
    setOutboundStatus(null);
    try {
      const res = await triggerOutboundCall(phoneNumber);
      setOutboundStatus({
        type: 'success',
        message: res.message || `Outbound phone call initiated to ${phoneNumber}!`
      });
    } catch (err) {
      setOutboundStatus({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to trigger outbound phone call.'
      });
    } finally {
      setIsDialing(false);
    }
  };

  const getStatusBadge = () => {
    switch (callStatus) {
      case 'connecting':
        return { label: 'Connecting WebRTC...', color: 'bg-amber-500/20 text-amber-300 border-amber-500/30' };
      case 'connected':
        return { label: 'Live Connection', color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' };
      case 'speaking':
        return { label: 'AI Agent Speaking', color: 'bg-brand-500/20 text-brand-300 border-brand-500/30 animate-pulse' };
      case 'listening':
        return { label: 'Listening to Prospect', color: 'bg-purple-500/20 text-purple-300 border-purple-500/30' };
      case 'ended':
        return { label: 'Call Ended - Processing Lead', color: 'bg-slate-700 text-slate-300 border-slate-600' };
      default:
        return { label: 'Ready for Call', color: 'bg-slate-800 text-slate-400 border-slate-700' };
    }
  };

  const badge = getStatusBadge();

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-xl mb-8">
      
      {/* Top Flex Controls Row */}
      <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
        
        {/* 1. Left Side: Call Controller Widget */}
        <div className="flex items-center gap-6 w-full lg:w-auto justify-between lg:justify-start">
          
          {/* Pulsing Phone Action Button */}
          <div className="relative">
            {isCalling && (
              <span className="absolute -inset-2 rounded-full bg-brand-500/30 animate-ping opacity-75" />
            )}
            <button
              onClick={isCalling ? onStopCall : onStartCall}
              className={`relative z-10 w-16 h-16 rounded-2xl flex items-center justify-center shadow-lg transition-all duration-300 ${
                isCalling
                  ? 'bg-rose-600 hover:bg-rose-700 text-white shadow-rose-600/40 hover:scale-105'
                  : 'bg-gradient-to-tr from-brand-500 via-indigo-500 to-purple-600 hover:from-brand-400 hover:to-purple-500 text-white shadow-brand-500/30 hover:scale-105'
              }`}
            >
              {isCalling ? <PhoneOff className="w-7 h-7" /> : <Phone className="w-7 h-7" />}
            </button>
          </div>

          {/* Info Block */}
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-lg font-bold text-white font-outfit">Vapi AI Voice Caller</h3>
              <span className={`text-[11px] font-medium px-2.5 py-0.5 rounded-full border ${badge.color}`}>
                {badge.label}
              </span>
            </div>
            
            <p className="text-xs text-slate-400 flex items-center gap-2">
              {isCalling ? (
                <>
                  <span className="font-mono text-brand-400 font-bold text-sm">{formatTime(callDuration)}</span>
                  <span>•</span>
                  <span>{isSimulation ? 'Interactive WebRTC Call' : 'WebRTC Live SDK'}</span>
                </>
              ) : (
                <span>Test browser voice calling or trigger an outbound phone call below</span>
              )}
            </p>
          </div>
        </div>

        {/* 2. Middle: Audio Visualizer Waveform & Mute Controls (During Call) */}
        {isCalling ? (
          <div className="flex items-center gap-4 w-full lg:w-auto justify-center">
            <div className="flex items-center gap-1 h-8 px-4 py-1.5 rounded-xl bg-slate-900/80 border border-slate-800">
              <Activity className="w-4 h-4 text-brand-400 mr-2" />
              {[0.4, 0.9, 0.5, 0.8, 0.3, 1.0, 0.6, 0.4, 0.7].map((height, i) => (
                <div
                  key={i}
                  className={`w-1 rounded-full bg-brand-400 transition-all duration-150 ${
                    callStatus === 'speaking' || callStatus === 'listening' ? 'animate-wave' : 'h-2'
                  }`}
                  style={{
                    height: callStatus === 'speaking' || callStatus === 'listening' ? `${height * 100}%` : '8px',
                    animationDelay: `${i * 0.15}s`,
                  }}
                />
              ))}
            </div>

            <button
              onClick={onToggleMute}
              className={`p-3 rounded-xl border transition-all ${
                isMuted
                  ? 'bg-rose-500/20 border-rose-500/40 text-rose-400'
                  : 'bg-slate-800 border-slate-700 text-slate-300 hover:text-white'
              }`}
              title={isMuted ? 'Unmute Microphone' : 'Mute Microphone'}
            >
              {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>

            <button
              onClick={onStopCall}
              className="px-4 py-2 text-xs font-bold text-rose-400 bg-rose-500/10 border border-rose-500/20 hover:bg-rose-500/20 rounded-xl transition-all"
            >
              End Call
            </button>
          </div>
        ) : null}

        {/* 3. Right: Outbound Telephony Dialer */}
        <div className="w-full lg:w-auto flex flex-col gap-2">
          <form onSubmit={handleOutboundPhoneCall} className="flex items-center gap-2">
            <div className="relative flex-1">
              <PhoneCall className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="tel"
                placeholder="Enter phone e.g. +923189663004"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
              />
            </div>
            <button
              type="submit"
              disabled={isDialing || !phoneNumber}
              className="px-4 py-2 rounded-xl bg-brand-500 hover:bg-brand-400 disabled:opacity-50 text-white font-semibold text-xs flex items-center gap-1.5 transition-all shadow-md shadow-brand-500/20"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{isDialing ? 'Dialing...' : 'Call Phone via Vapi'}</span>
            </button>
          </form>

          {/* Quick Member Preset Chip */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-slate-400">Quick Member:</span>
            <button
              type="button"
              onClick={() => setPhoneNumber('+923189663004')}
              className="text-[11px] font-semibold text-brand-400 hover:text-brand-300 bg-brand-500/10 hover:bg-brand-500/20 border border-brand-500/20 px-2.5 py-0.5 rounded-full transition-all"
            >
              👤 Muhammad Saad (+923189663004)
            </button>
          </div>

          {outboundStatus && (
            <p className={`text-[11px] font-medium ${outboundStatus.type === 'success' ? 'text-emerald-400' : 'text-rose-400'}`}>
              {outboundStatus.message}
            </p>
          )}
        </div>

      </div>

      {/* Real-time Call Transcript Feed */}
      {transcripts.length > 0 && (
        <div className="mt-5 pt-4 border-t border-slate-800/80">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <MessageSquare className="w-3.5 h-3.5 text-brand-400" />
              Live Conversation Feed
            </span>
            <span className="text-[10px] text-slate-500">{transcripts.length} Turns</span>
          </div>

          <div className="max-h-36 overflow-y-auto space-y-2 pr-2">
            {transcripts.map((t, idx) => (
              <div
                key={idx}
                className={`p-2.5 rounded-xl text-xs flex flex-col gap-0.5 ${
                  t.role === 'assistant'
                    ? 'bg-brand-500/10 border border-brand-500/20 text-slate-200 ml-0 mr-8'
                    : 'bg-slate-800/80 border border-slate-700 text-slate-200 ml-8 mr-0'
                }`}
              >
                <div className="flex items-center justify-between text-[10px] font-semibold mb-1">
                  <span className={t.role === 'assistant' ? 'text-brand-400 font-bold' : 'text-purple-400 font-bold'}>
                    {t.role === 'assistant' ? '🤖 Voice AI Agent' : '👤 Prospect'}
                  </span>
                  <span className="text-slate-500">{t.timestamp}</span>
                </div>
                <p className="leading-relaxed">{t.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
