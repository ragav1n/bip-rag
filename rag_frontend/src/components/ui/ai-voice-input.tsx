"use client";

import { Mic } from "lucide-react";
import { useState, useEffect, useRef, useCallback } from "react";
import { cn } from "@/lib/utils";

// Minimal Web Speech API types (not yet stable in TypeScript's DOM lib)
interface SpeechRecognitionResult {
  readonly isFinal: boolean;
  readonly length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
}
interface SpeechRecognitionAlternative {
  readonly transcript: string;
  readonly confidence: number;
}
interface SpeechRecognitionResultList {
  readonly length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}
interface SpeechRecognitionEvent extends Event {
  readonly resultIndex: number;
  readonly results: SpeechRecognitionResultList;
}
interface ISpeechRecognition extends EventTarget {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  onresult: ((e: SpeechRecognitionEvent) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
}
type SpeechRecognitionConstructor = new () => ISpeechRecognition;

interface AIVoiceInputProps {
  onStart?: () => void;
  onStop?: (duration: number) => void;
  onTranscript?: (text: string) => void;
  onLiveTranscript?: (text: string) => void;
  language?: 'en' | 'de';
  visualizerBars?: number;
  className?: string;
}

export function AIVoiceInput({
  onStart,
  onStop,
  onTranscript,
  onLiveTranscript,
  language = 'en',
  visualizerBars = 48,
  className,
}: AIVoiceInputProps) {
  const [recording, setRecording] = useState(false);
  const [time, setTime] = useState(0);
  const [micDenied, setMicDenied] = useState(false);

  // DOM refs for bars — direct mutation bypasses React re-renders at 60fps
  const barRefs = useRef<(HTMLDivElement | null)[]>([]);

  const recognitionRef = useRef<ISpeechRecognition | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number>(0);
  const finalTranscriptRef = useRef("");
  // Pre-calculated frequency bin indices (logarithmic, voice range 80 Hz – 5 kHz)
  const binIndicesRef = useRef<number[]>([]);

  // Timer
  useEffect(() => {
    if (!recording) { setTime(0); return; }
    const id = setInterval(() => setTime((t) => t + 1), 1000);
    return () => clearInterval(id);
  }, [recording]);

  // Build logarithmic bin index map once per fftSize
  const buildBinIndices = useCallback((fftSize: number, sampleRate: number) => {
    const binCount = fftSize / 2;
    const hzPerBin = sampleRate / fftSize;
    const minHz = 80;
    const maxHz = 5000;
    const minBin = Math.max(1, Math.round(minHz / hzPerBin));
    const maxBin = Math.min(binCount - 1, Math.round(maxHz / hzPerBin));
    const logMin = Math.log(minBin);
    const logMax = Math.log(maxBin);
    binIndicesRef.current = Array.from({ length: visualizerBars }, (_, i) => {
      const t = i / (visualizerBars - 1);
      return Math.round(Math.exp(logMin + t * (logMax - logMin)));
    });
  }, [visualizerBars]);

  // Per-bar smoothed values for silky interpolation between frames
  const smoothedRef = useRef<number[]>([]);

  // Animate bars directly via DOM refs — no React state, no re-renders
  const startVisualizer = useCallback((analyser: AnalyserNode) => {
    const data = new Uint8Array(analyser.frequencyBinCount);
    const idleHeight = 0.04;
    const lerpUp = 0.22;    // attack — rises quickly to catch speech onset
    const lerpDown = 0.08;  // release — falls slowly for smooth decay

    // Initialise smoothed array
    if (smoothedRef.current.length !== visualizerBars) {
      smoothedRef.current = new Array(visualizerBars).fill(0);
    }

    const tick = () => {
      analyser.getByteFrequencyData(data);
      const smoothed = smoothedRef.current;
      barRefs.current.forEach((bar, i) => {
        if (!bar) return;
        const bin = binIndicesRef.current[i] ?? i;
        const target = data[bin] / 255;
        // Asymmetric lerp: fast attack, slow release → natural breathing feel
        const lerp = target > smoothed[i] ? lerpUp : lerpDown;
        smoothed[i] += (target - smoothed[i]) * lerp;
        const scale = Math.max(idleHeight, smoothed[i]);
        bar.style.transform = `scaleY(${scale})`;
        bar.style.opacity = String(Math.max(0.25, 0.3 + smoothed[i] * 0.7));
      });
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
  }, [visualizerBars]);

  // Reset bars to idle state
  const resetBars = useCallback(() => {
    smoothedRef.current = [];
    barRefs.current.forEach((bar) => {
      if (!bar) return;
      bar.style.transform = "scaleY(0.04)";
      bar.style.opacity = "0.2";
    });
  }, []);

  const stopAll = useCallback(() => {
    // Null recognition ref BEFORE calling stop() so onend doesn't restart
    const rec = recognitionRef.current;
    recognitionRef.current = null;
    rec?.stop();

    cancelAnimationFrame(rafRef.current);
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;

    // Disconnect before closing to avoid "AudioContext is closed" errors
    analyserRef.current?.disconnect();
    analyserRef.current = null;
    audioCtxRef.current?.close();
    audioCtxRef.current = null;

    resetBars();
  }, [resetBars]);

  useEffect(() => () => stopAll(), [stopAll]);

  const handleClick = async () => {
    if (recording) {
      const final = finalTranscriptRef.current;
      stopAll();
      setRecording(false);
      onStop?.(time);
      if (final) onTranscript?.(final);
      return;
    }

    setMicDenied(false);
    finalTranscriptRef.current = "";
    setRecording(true);

    // ── 1. Microphone + Web Audio visualizer ─────────────────────────────
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const audioCtx = new AudioContext();
      audioCtxRef.current = audioCtx;

      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;                  // 128 frequency bins
      analyser.smoothingTimeConstant = 0.88;   // heavier damping for fluid motion
      audioCtx.createMediaStreamSource(stream).connect(analyser);
      analyserRef.current = analyser;

      buildBinIndices(analyser.fftSize, audioCtx.sampleRate);
      startVisualizer(analyser);
    } catch {
      setMicDenied(true);
      // Visualizer won't animate but speech recognition still works below
    }

    // ── 2. Speech recognition ─────────────────────────────────────────────
    const SpeechRecognitionAPI = (
      (window as unknown as { SpeechRecognition?: SpeechRecognitionConstructor }).SpeechRecognition ??
      (window as unknown as { webkitSpeechRecognition?: SpeechRecognitionConstructor }).webkitSpeechRecognition
    );
    if (!SpeechRecognitionAPI) return;

    const recognition = new SpeechRecognitionAPI();
    recognition.lang = language === 'de' ? 'de-DE' : 'en-US';
    recognition.interimResults = true;
    recognition.continuous = true;

    recognition.onresult = (e: SpeechRecognitionEvent) => {
      let newFinal = "";
      let interim = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) newFinal += e.results[i][0].transcript;
        else interim += e.results[i][0].transcript;
      }
      finalTranscriptRef.current += newFinal;
      onLiveTranscript?.(finalTranscriptRef.current + interim);
    };

    // Continuous mode can auto-end on silence — restart if still supposed to be recording
    recognition.onend = () => {
      if (recognitionRef.current === recognition) {
        setTimeout(() => {
          try { recognition.start(); } catch { /* mic removed or permission revoked */ }
        }, 150);
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
    onStart?.();
  };

  const formatTime = (s: number) =>
    `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

  return (
    <div className={cn("w-full py-4", className)}>
      <div className="w-full mx-auto flex items-center flex-col gap-2">

        <button
          className="w-16 h-16 rounded-xl flex items-center justify-center transition-colors hover:bg-white/5"
          type="button"
          onClick={handleClick}
        >
          {recording ? (
            <div
              className="w-6 h-6 rounded-sm animate-spin"
              style={{ background: "#F56B00", animationDuration: "3s" }}
            />
          ) : (
            <Mic className="w-6 h-6" style={{ color: micDenied ? "#ef4444" : "#F56B00", opacity: 0.8 }} />
          )}
        </button>

        <span
          className="font-mono text-sm transition-opacity duration-300"
          style={{ color: "#E8F4FD", opacity: recording ? 0.7 : 0.3 }}
        >
          {formatTime(time)}
        </span>

        {/* Industry-standard symmetric visualizer — bars grow from center (scaleY) */}
        <div className="h-12 w-full flex items-center justify-center gap-[2px]">
          {Array.from({ length: visualizerBars }).map((_, i) => (
            <div
              key={i}
              ref={(el) => { barRefs.current[i] = el; }}
              className="w-[3px] rounded-full"
              style={{
                height: "100%",
                background: "#F56B00",
                opacity: 0.2,
                transform: "scaleY(0.04)",
                transformOrigin: "center",
                // No CSS transition — smoothingTimeConstant handles damping at audio level
              }}
            />
          ))}
        </div>

        {micDenied ? (
          <p className="text-xs" style={{ color: "rgba(239,68,68,0.7)" }}>
            Microphone access denied
          </p>
        ) : (
          <p className="text-xs" style={{ color: "rgba(208,207,201,0.5)" }}>
            {recording ? "Listening… (click to stop)" : "Click to speak"}
          </p>
        )}
      </div>
    </div>
  );
}
