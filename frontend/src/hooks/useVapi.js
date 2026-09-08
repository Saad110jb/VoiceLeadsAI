import { useState, useEffect, useRef, useCallback } from 'react';
import Vapi from '@vapi-ai/web';
import { simulateCall } from '../services/api';

const PUBLIC_KEY = import.meta.env.VITE_VAPI_PUBLIC_KEY || '';
const ASSISTANT_ID = import.meta.env.VITE_VAPI_ASSISTANT_ID || '';

export function useVapi() {
  const [isCalling, setIsCalling] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [callStatus, setCallStatus] = useState('idle'); // idle, connecting, connected, speaking, listening, ended
  const [transcripts, setTranscripts] = useState([]);
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [callDuration, setCallDuration] = useState(0);
  const [isSimulation, setIsSimulation] = useState(false);

  const vapiRef = useRef(null);
  const timerRef = useRef(null);

  // Initialize Vapi SDK safely
  useEffect(() => {
    if (PUBLIC_KEY && PUBLIC_KEY !== 'your_vapi_public_key') {
      try {
        const vapiInstance = new Vapi(PUBLIC_KEY);
        vapiRef.current = vapiInstance;

        vapiInstance.on('call-start', () => {
          setIsCalling(true);
          setCallStatus('connected');
          startTimer();
        });

        vapiInstance.on('call-end', () => {
          setIsCalling(false);
          setCallStatus('ended');
          stopTimer();
        });

        vapiInstance.on('speech-start', () => {
          setCallStatus('speaking');
        });

        vapiInstance.on('speech-end', () => {
          setCallStatus('listening');
        });

        vapiInstance.on('volume-level', (volume) => {
          setVolumeLevel(volume);
        });

        vapiInstance.on('message', (message) => {
          if (message.type === 'transcript' && message.transcript) {
            setTranscripts((prev) => [
              ...prev,
              {
                role: message.role || (message.transcriptType === 'final' ? 'user' : 'assistant'),
                text: message.transcript,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              },
            ]);
          }
        });

        vapiInstance.on('error', (err) => {
          console.error('Vapi WebRTC Error:', err);
          setCallStatus('idle');
          setIsCalling(false);
        });
      } catch (e) {
        console.warn('Vapi SDK init error:', e);
      }
    }
    return () => {
      stopTimer();
    };
  }, []);

  const startTimer = () => {
    setCallDuration(0);
    timerRef.current = setInterval(() => {
      setCallDuration((prev) => prev + 1);
    }, 1000);
  };

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const startCall = useCallback(async () => {
    setTranscripts([]);
    setCallDuration(0);

    // If Vapi credentials are ready, start real WebRTC call
    if (vapiRef.current && ASSISTANT_ID && ASSISTANT_ID !== 'your_assistant_id') {
      try {
        setCallStatus('connecting');
        setIsSimulation(false);
        await vapiRef.current.start(ASSISTANT_ID);
      } catch (err) {
        console.error('Failed to start Vapi call:', err);
        startSimulationCall();
      }
    } else {
      // Automatic simulation mode for instant evaluation
      startSimulationCall();
    }
  }, []);

  const startSimulationCall = () => {
    setIsSimulation(true);
    setIsCalling(true);
    setCallStatus('connecting');

    setTimeout(() => {
      setCallStatus('connected');
      startTimer();

      // Simulated agent greeting
      setTranscripts([
        {
          role: 'assistant',
          text: 'Hello! Thank you for calling VoiceLeads AI. I am your automated sales assistant. How can I help your enterprise today?',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);

      // Simulated user response
      setTimeout(() => {
        setCallStatus('listening');
        setTranscripts((prev) => [
          ...prev,
          {
            role: 'user',
            text: 'Hi, we need to handle 300 incoming sales calls per day and sync qualified leads directly into Google Sheets and n8n.',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);

        // Simulated follow-up
        setTimeout(() => {
          setCallStatus('speaking');
          setTranscripts((prev) => [
            ...prev,
            {
              role: 'assistant',
              text: 'That sounds like a great fit for our VocalSync pipeline. What is your estimated timeline for deployment?',
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            },
          ]);

          setTimeout(() => {
            setTranscripts((prev) => [
              ...prev,
              {
                role: 'user',
                text: 'We want to start immediately within this week. Our budget is around $25,000.',
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              },
            ]);
          }, 3000);
        }, 3000);
      }, 2500);
    }, 1500);
  };

  const stopCall = useCallback(async () => {
    stopTimer();
    setCallStatus('ended');

    if (vapiRef.current && !isSimulation) {
      try {
        vapiRef.current.stop();
      } catch (e) {
        console.error('Error stopping Vapi call:', e);
      }
    }

    setIsCalling(false);

    // If in simulation mode, post simulated lead to backend
    if (isSimulation && transcripts.length > 0) {
      const fullText = transcripts.map((t) => `${t.role}: ${t.text}`).join('\n');
      try {
        await simulateCall({
          name: 'Alexis Vance',
          company: 'Nexus Scale Labs',
          transcript: fullText,
          summary: 'Inquired about 300 daily call lead handling with immediate $25k budget.',
        });
      } catch (err) {
        console.error('Failed to post simulated call lead:', err);
      }
    }

    setTimeout(() => {
      setCallStatus('idle');
    }, 2000);
  }, [isSimulation, transcripts]);

  const toggleMute = useCallback(() => {
    if (vapiRef.current && !isSimulation) {
      const newMute = !isMuted;
      vapiRef.current.setMuted(newMute);
      setIsMuted(newMute);
    } else {
      setIsMuted((prev) => !prev);
    }
  }, [isMuted, isSimulation]);

  return {
    isCalling,
    isMuted,
    callStatus,
    transcripts,
    volumeLevel,
    callDuration,
    isSimulation,
    startCall,
    stopCall,
    toggleMute,
  };
}
