"use client";

import { CornerRightUp } from "lucide-react";
import { useState, useEffect } from "react";
import React from "react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { useAutoResizeTextarea } from "@/components/hooks/use-auto-resize-textarea";

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

  return (
    <div className={cn("w-full", className)}>
      {/* Outer box — flex column so nothing overlaps */}
      <div
        className="w-full rounded-2xl flex flex-col transition-all duration-200"
        style={{ background: '#202B21', border: '1px solid rgba(111,116,105,0.2)' }}
        onFocus={e => (e.currentTarget.style.borderColor = 'rgba(100,168,89,0.4)')}
        onBlur={e => (e.currentTarget.style.borderColor = 'rgba(111,116,105,0.2)')}
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
            color: '#D0CFC9',
            caretColor: '#64A859',
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

        {/* Bottom bar — toolbar left, submit right */}
        <div className="flex items-center justify-between px-3 pb-3 pt-1 gap-2">
          <div className="flex-1">{toolbar ?? null}</div>

          <button
            onClick={handleSubmit}
            className="rounded-xl p-1.5 transition-all duration-200 flex-shrink-0"
            style={
              submitted
                ? { background: 'transparent' }
                : {
                    background: inputValue.trim() ? '#64A859' : 'rgba(100,168,89,0.15)',
                    boxShadow: inputValue.trim() ? '0 4px 14px rgba(100,168,89,0.3)' : 'none',
                  }
            }
            type="button"
            disabled={submitted}
          >
            {submitted ? (
              <div
                className="w-4 h-4 rounded-sm animate-spin"
                style={{ background: '#64A859', animationDuration: '1.5s' }}
              />
            ) : (
              <CornerRightUp
                className="w-4 h-4"
                style={{
                  color: inputValue.trim() ? '#101010' : '#64A859',
                  opacity: inputValue.trim() ? 1 : 0.5,
                }}
              />
            )}
          </button>
        </div>
      </div>

      {/* Status line */}
      <p
        className="mt-1.5 h-4 text-xs text-center"
        style={{ color: submitted ? '#64A859' : 'transparent' }}
      >
        Searching documents…
      </p>
    </div>
  );
}
