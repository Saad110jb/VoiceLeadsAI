import { useState, useEffect, useCallback } from 'react';
import { getLeads, getLeadStats, deleteLead, relayToN8n, simulateCall } from '../services/api';

export function useLeads(pollIntervalSeconds = 5) {
  const [leads, setLeads] = useState([]);
  const [stats, setStats] = useState({
    total_leads: 0,
    hot_leads: 0,
    warm_leads: 0,
    cold_leads: 0,
    conversion_rate: 0,
    avg_call_duration_seconds: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterTemp, setFilterTemp] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchAllData = useCallback(async () => {
    try {
      const [leadsData, statsData] = await Promise.all([
        getLeads(filterTemp, searchQuery),
        getLeadStats(),
      ]);
      setLeads(leadsData);
      setStats(statsData);
      setError(null);
    } catch (err) {
      console.error('Error fetching leads:', err);
      setError('Failed to sync with backend server. Check if FastAPI is running.');
    } finally {
      setLoading(false);
    }
  }, [filterTemp, searchQuery]);

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(() => {
      fetchAllData();
    }, pollIntervalSeconds * 1000);

    return () => clearInterval(interval);
  }, [fetchAllData, pollIntervalSeconds]);

  const handleDelete = async (id) => {
    try {
      await deleteLead(id);
      await fetchAllData();
    } catch (err) {
      console.error('Error deleting lead:', err);
    }
  };

  const handleRelay = async (lead) => {
    try {
      await relayToN8n(lead);
      await fetchAllData();
    } catch (err) {
      console.error('Error relaying lead:', err);
    }
  };

  const handleSimulateCall = async () => {
    try {
      await simulateCall();
      await fetchAllData();
    } catch (err) {
      console.error('Error triggering call simulation:', err);
    }
  };

  return {
    leads,
    stats,
    loading,
    error,
    filterTemp,
    setFilterTemp,
    searchQuery,
    setSearchQuery,
    refetch: fetchAllData,
    deleteLead: handleDelete,
    relayLead: handleRelay,
    simulateCall: handleSimulateCall,
  };
}
