"use client";

import { CornerRightUp, Mic } from "lucide-react";
import { useState, useEffect } from "react";
import React from "react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { useAutoResizeTextarea } from "@/components/hooks/use-auto-resize-textarea";
import { AIVoiceInput } from "@/components/ui/ai-voice-input";
import { AnimatePresence, motion } from "framer-motion";

interface AIInputWithLoadingProps {
  id?: string;
  placeholder?: string;
  minHeight?: number;
  maxHeight?: number;
  loadingDuration?: number;
  thinkingDuration?: number;
  onSubmit?: (value: string) => void | Promise<void>;
  className?: string;
  autoAnimate?: boolean;
  toolbar?: React.ReactNode;
}

export function AIInputWithLoading({
  id = "ai-input-with-loading",
  placeholder = "Ask me anything!",
  minHeight = 56,
  maxHeight = 200,
  loadingDuration = 0,
  thinkingDuration = 1000,
  onSubmit,
  className,
  autoAnimate = false,
  toolbar,
}: AIInputWithLoadingProps) {
  const [inputValue, setInputValue] = useState("");
  const [submitted, setSubmitted] = useState(autoAnimate);
  const [isAnimating] = useState(autoAnimate);
  const [showVoice, setShowVoice] = useState(false);
  // Text that was in the box before voice recording started — live transcript appends to it
  const preVoiceTextRef = React.useRef("");

  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight,
    maxHeight,
  });

  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;
    const runAnimation = () => {
      if (!isAnimating) return;
      setSubmitted(true);
      timeoutId = setTimeout(() => {
        setSubmitted(false);
        timeoutId = setTimeout(runAnimation, thinkingDuration);
      }, loadingDuration);
    };
    if (isAnimating) runAnimation();
    return () => clearTimeout(timeoutId);
  }, [isAnimating, loadingDuration, thinkingDuration]);

  const handleSubmit = async () => {
    if (!inputValue.trim() || submitted) return;
    setSubmitted(true);
    await onSubmit?.(inputValue);
    setInputValue("");
    adjustHeight(true);
    setTimeout(() => setSubmitted(false), loadingDuration);
  };

  const handleVoiceStart = () => {
    preVoiceTextRef.current = inputValue.trimEnd();
  };

  // Called on every interim result — types words live into the textarea
  const handleLiveTranscript = (liveText: string) => {
    const base = preVoiceTextRef.current;
    setInputValue(base ? `${base} ${liveText}` : liveText);
    adjustHeight();
  };

  // Called once when recording stops — commit the clean final transcript
  const handleTranscript = (finalText: string) => {
    const base = preVoiceTextRef.current;
    setInputValue(base ? `${base} ${finalText}` : finalText);
    adjustHeight();
    setShowVoice(false);
    setTimeout(() => textareaRef.current?.focus(), 50);
  };

  return (
    <div className={cn("w-full", className)}>
      {/* Voice input overlay */}
      <AnimatePresence>
        {showVoice && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.97 }}
            transition={{ duration: 0.2 }}
            className="mb-2 rounded-2xl overflow-hidden"
            style={{ background: '#06042e', border: '1px solid rgba(245,107,0,0.25)' }}
          >
            <AIVoiceInput
              onStart={handleVoiceStart}
              onLiveTranscript={handleLiveTranscript}
              onTranscript={handleTranscript}
              className="py-3"
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Outer box — flex column so nothing overlaps */}
      <div
        className="w-full rounded-2xl flex flex-col transition-all duration-200"
        style={{ background: '#0c0a52', border: '1px solid rgba(125,198,233,0.2)' }}
        onFocus={e => (e.currentTarget.style.borderColor = 'rgba(245,107,0,0.4)')}
        onBlur={e => (e.currentTarget.style.borderColor = 'rgba(125,198,233,0.2)')}
      >
        {/* Textarea — no padding tricks needed */}
        <Textarea
          id={id}
          placeholder={placeholder}
          className={cn(
            "w-full px-5 pt-4 pb-2",
            "resize-none text-wrap leading-[1.2]",
            "border-none focus-visible:ring-0 outline-none rounded-t-2xl",
            `min-h-[${minHeight}px]`
          )}
          style={{
            background: 'transparent',
            color: '#E8F4FD',
            caretColor: '#F56B00',
          }}
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value);
            adjustHeight();
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
          disabled={submitted}
        />

        {/* Bottom bar — toolbar left, mic + submit right */}
        <div className="flex items-center justify-between px-3 pb-3 pt-1 gap-2">
          <div className="flex-1">{toolbar ?? null}</div>

          {/* Mic button */}
          <button
            onClick={() => setShowVoice((v) => !v)}
            className="rounded-xl p-1.5 transition-all duration-200 flex-shrink-0"
            style={
              showVoice
                ? { background: 'rgba(245,107,0,0.2)', boxShadow: '0 0 0 1.5px rgba(245,107,0,0.5)' }
                : { background: 'rgba(245,107,0,0.08)' }
            }
            type="button"
            title="Voice input"
          >
            <Mic
              className="w-4 h-4"
              style={{ color: '#F56B00', opacity: showVoice ? 1 : 0.6 }}
            />
          </button>

          {/* Submit button */}
          <button
            onClick={handleSubmit}
            className="rounded-xl p-1.5 transition-all duration-200 flex-shrink-0"
            style={
              submitted
                ? { background: 'transparent' }
                : {
                    background: inputValue.trim() ? '#F56B00' : 'rgba(245,107,0,0.15)',
                    boxShadow: inputValue.trim() ? '0 4px 14px rgba(245,107,0,0.3)' : 'none',
                  }
            }
            type="button"
            disabled={submitted}
          >
            {submitted ? (
              <div
                className="w-4 h-4 rounded-sm animate-spin"
                style={{ background: '#F56B00', animationDuration: '1.5s' }}
              />
            ) : (
              <CornerRightUp
                className="w-4 h-4"
                style={{
                  color: inputValue.trim() ? '#ffffff' : '#F56B00',
                  opacity: inputValue.trim() ? 1 : 0.5,
                }}
              />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
