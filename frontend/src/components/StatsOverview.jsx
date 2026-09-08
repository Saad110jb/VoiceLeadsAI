import React from 'react';
import { Flame, Sun, Snowflake, PhoneCall, TrendingUp, Clock } from 'lucide-react';

export function StatsOverview({ stats, activeFilter, onFilterChange }) {
  const cards = [
    {
      id: '',
      title: 'Total Call Volume',
      value: stats.total_leads || 0,
      subtext: 'Processed Inbound & WebRTC',
      icon: PhoneCall,
      color: 'text-brand-400',
      bgColor: 'bg-brand-500/10',
      borderColor: 'border-brand-500/20',
    },
    {
      id: 'HOT',
      title: 'Hot Leads',
      value: stats.hot_leads || 0,
      subtext: 'High Intent / Budget Ready',
      icon: Flame,
      color: 'text-rose-400',
      bgColor: 'bg-rose-500/10',
      borderColor: 'border-rose-500/20',
      glow: 'glow-red'
    },
    {
      id: 'WARM',
      title: 'Warm Prospects',
      value: stats.warm_leads || 0,
      subtext: 'Evaluating & Seeking Demo',
      icon: Sun,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/20',
    },
    {
      id: 'COLD',
      title: 'Cold / Inquiries',
      value: stats.cold_leads || 0,
      subtext: 'Unqualified or Support',
      icon: Snowflake,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20',
    },
    {
      id: 'CONVERSION',
      title: 'Conversion Rate',
      value: `${stats.conversion_rate || 0}%`,
      subtext: 'Qualified / Total Ratio',
      icon: TrendingUp,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/20',
    },
    {
      id: 'DURATION',
      title: 'Avg Call Duration',
      value: `${stats.avg_call_duration_seconds || 0}s`,
      subtext: 'Talk time per conversation',
      icon: Clock,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/20',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
      {cards.map((card) => {
        const Icon = card.icon;
        const isActive = activeFilter === card.id && card.id !== '' && card.id !== 'CONVERSION' && card.id !== 'DURATION';
        const isClickable = ['HOT', 'WARM', 'COLD', ''].includes(card.id);

        return (
          <div
            key={card.title}
            onClick={() => isClickable && onFilterChange(card.id === activeFilter ? '' : card.id)}
            className={`p-4 rounded-xl glass-panel glass-card-hover border transition-all cursor-pointer ${card.borderColor} ${
              isActive ? 'ring-2 ring-brand-400 bg-slate-850' : ''
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-400">{card.title}</span>
              <div className={`p-2 rounded-lg ${card.bgColor}`}>
                <Icon className={`w-4 h-4 ${card.color}`} />
              </div>
            </div>
            <div className="text-2xl font-bold text-white tracking-tight font-outfit mb-1">
              {card.value}
            </div>
            <div className="text-[11px] text-slate-400 truncate">
              {card.subtext}
            </div>
          </div>
        );
      })}
    </div>
  );
}
