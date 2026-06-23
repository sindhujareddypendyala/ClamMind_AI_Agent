import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Square, X, Loader2, Volume2 } from 'lucide-react';
import { voiceAPI } from '../services/api';

// Helper to encode raw PCM float samples into a 16-bit mono WAV buffer
function bufferToWav(buffer, sampleRate) {
  const numOfChan = 1;
  const length = buffer.length * 2 + 44;
  const bufferArr = new ArrayBuffer(length);
  const view = new DataView(bufferArr);
  let pos = 0;

  const setUint16 = (data) => {
    view.setUint16(pos, data, true);
    pos += 2;
  };

  const setUint32 = (data) => {
    view.setUint32(pos, data, true);
    pos += 4;
  };

  // RIFF identifier
  setUint32(0x46464952); // "RIFF"
  setUint32(length - 8); // file length - 8
  setUint32(0x45564157); // "WAVE"

  // format chunk identifier
  setUint32(0x20746d66); // "fmt "
  setUint32(16);         // format chunk length
  setUint16(1);          // sample format (raw PCM)
  setUint16(numOfChan);  // channel count
  setUint32(sampleRate); // sample rate
  setUint32(sampleRate * 2); // byte rate
  setUint16(2);          // block align
  setUint16(16);         // bits per sample

  // data chunk identifier
  setUint32(0x61746164); // "data"
  setUint32(length - pos - 4); // data chunk length

  // write PCM audio samples
  for (let i = 0; i < buffer.length; i++) {
    const sample = Math.max(-1, Math.min(1, buffer[i]));
    const intSample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
    view.setInt16(pos, intSample, true);
    pos += 2;
  }

  return new Blob([bufferArr], { type: 'audio/wav' });
}

export default function VoiceModal({ isOpen, onClose, onTranscriptionComplete }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [error, setError] = useState(null);
  
  const audioContextRef = useRef(null);
  const scriptProcessorRef = useRef(null);
  const sourceRef = useRef(null);
  const streamRef = useRef(null);
  const samplesRef = useRef([]);
  const recordingIdRef = useRef(null);

  const startRecording = async () => {
    setError(null);
    samplesRef.current = [];
    recordingIdRef.current = `rec_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      const audioContext = new AudioContextClass();
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);
      sourceRef.current = source;

      // ScriptProcessor with buffer size 2048, 1 input channel, 1 output channel
      const scriptProcessor = audioContext.createScriptProcessor(2048, 1, 1);
      scriptProcessorRef.current = scriptProcessor;

      scriptProcessor.onaudioprocess = (event) => {
        const inputBuffer = event.inputBuffer;
        const inputData = inputBuffer.getChannelData(0);
        // Copy audio sample floats
        samplesRef.current.push(...inputData);
      };

      source.connect(scriptProcessor);
      scriptProcessor.connect(audioContext.destination);

      setIsRecording(true);
    } catch (err) {
      console.error(err);
      setError('Microphone access denied or audio device not found.');
    }
  };

  const stopRecording = () => {
    if (isRecording) {
      // Disconnect audio routing
      if (scriptProcessorRef.current) {
        scriptProcessorRef.current.disconnect();
        scriptProcessorRef.current.onaudioprocess = null;
      }
      if (sourceRef.current) {
        sourceRef.current.disconnect();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }

      const sampleRate = audioContextRef.current ? audioContextRef.current.sampleRate : 44100;

      if (audioContextRef.current) {
        audioContextRef.current.close();
      }

      // Convert captured PCM floats to mono WAV Blob
      const wavBlob = bufferToWav(samplesRef.current, sampleRate);
      setIsRecording(false);
      handleAudioUpload(wavBlob);
    }
  };

  const handleCancel = () => {
    // Stop tracks and close nodes
    if (scriptProcessorRef.current) {
      scriptProcessorRef.current.disconnect();
      scriptProcessorRef.current.onaudioprocess = null;
    }
    if (sourceRef.current) {
      sourceRef.current.disconnect();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    setIsRecording(false);
    setIsTranscribing(false);
    onClose();
  };

  const handleAudioUpload = async (audioBlob) => {
    setIsTranscribing(true);
    setError(null);
    
    try {
      const file = new File([audioBlob], `${recordingIdRef.current}.wav`, { type: 'audio/wav' });
      const formData = new FormData();
      formData.append('file', file);
      
      const data = await voiceAPI.transcribeAudio(formData);
      if (data.status === 'success') {
        // Enforce inserting into input bar without auto-sending
        if (data.transcript && !data.transcript.startsWith("Could not process audio") && !data.transcript.startsWith("Speech was unclear")) {
          onTranscriptionComplete(data.transcript);
          onClose();
        } else {
          setError(data.transcript || 'Speech recognition failed.');
        }
      } else {
        setError('Could not transcribe audio. Please try again.');
      }
    } catch (err) {
      console.error(err);
      setError('Transcription failed. Please check your connection or try typing.');
    } finally {
      setIsTranscribing(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="relative w-full max-w-md p-8 rounded-3xl glassmorphism shadow-2xl border border-white/20 text-center mx-4"
        >
          <button 
            onClick={handleCancel} 
            className="absolute top-4 right-4 p-2 rounded-full hover:bg-lightGreen text-gray-500 transition-colors"
          >
            <X size={20} />
          </button>
          
          <h3 className="text-2xl font-serif text-darkGreen font-semibold mb-2">Voice Companion</h3>
          <p className="text-sm text-accentGreen mb-8">
            Speak naturally. We will transcribe and insert it into your input field.
          </p>

          <div className="flex flex-col items-center justify-center mb-8">
            <div className="relative flex items-center justify-center w-36 h-36 rounded-full bg-lightGreen border border-borderGreen mb-6">
              {isRecording && (
                <>
                  <motion.div 
                    animate={{ scale: [1, 1.4, 1] }}
                    transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}
                    className="absolute inset-0 rounded-full bg-primaryGreen/10"
                  />
                  <motion.div 
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 1.2, ease: "easeInOut", delay: 0.3 }}
                    className="absolute inset-2 rounded-full bg-primaryGreen/25"
                  />
                </>
              )}
              
              <div className="z-10 flex items-center justify-center w-24 h-24 rounded-full bg-primaryGreen text-white shadow-lg">
                {isTranscribing ? (
                  <Loader2 size={36} className="animate-spin" />
                ) : isRecording ? (
                  <Volume2 size={36} />
                ) : (
                  <Mic size={36} />
                )}
              </div>
            </div>

            <div className="text-lg font-medium text-darkGreen min-h-[28px] mb-4">
              {isRecording ? "Listening..." : isTranscribing ? "Transcribing your voice..." : "Ready to record"}
            </div>
            
            {error && (
              <div className="text-red-500 text-sm px-4 mb-2">
                ⚠️ {error}
              </div>
            )}
          </div>

          <div className="flex items-center justify-center gap-4">
            {!isRecording && !isTranscribing ? (
              <button
                onClick={startRecording}
                className="flex items-center gap-2 px-6 py-3 rounded-full bg-primaryGreen text-white font-medium hover:bg-darkGreen transition-all shadow-md"
              >
                <Mic size={18} /> Start Recording
              </button>
            ) : isRecording ? (
              <button
                onClick={stopRecording}
                className="flex items-center gap-2 px-6 py-3 rounded-full bg-red-500 text-white font-medium hover:bg-red-600 transition-all shadow-md"
              >
                <Square size={18} /> Stop & Transcribe
              </button>
            ) : (
              <button
                disabled
                className="flex items-center gap-2 px-6 py-3 rounded-full bg-gray-300 text-gray-500 font-medium cursor-not-allowed"
              >
                <Loader2 size={18} className="animate-spin" /> Processing
              </button>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
