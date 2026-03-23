"use client";

import { CornerRightUp } from "lucide-react";
import { useState, useEffect } from "react";
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
      <div className="relative w-full">
        <div className="relative w-full">
          <Textarea
            id={id}
            placeholder={placeholder}
            className={cn(
              "w-full rounded-2xl pl-5 pr-12 py-4",
              "resize-none text-wrap leading-[1.2]",
              "border-none focus-visible:ring-1",
              `min-h-[${minHeight}px]`
            )}
            style={{
              background: '#202B21',
              color: '#D0CFC9',
              caretColor: '#64A859',
              // @ts-ignore
              '--tw-ring-color': 'rgba(100,168,89,0.4)',
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

          {/* Submit / loading button */}
          <button
            onClick={handleSubmit}
            className="absolute right-3 top-1/2 -translate-y-1/2 rounded-xl py-1.5 px-1.5 transition-all duration-200"
            style={
              submitted
                ? { background: 'transparent' }
                : {
                    background: inputValue.trim()
                      ? '#64A859'
                      : 'rgba(100,168,89,0.15)',
                    boxShadow: inputValue.trim()
                      ? '0 4px 14px rgba(100,168,89,0.3)'
                      : 'none',
                  }
            }
            type="button"
            disabled={submitted}
          >
            {submitted ? (
              <div
                className="w-4 h-4 rounded-sm animate-spin"
                style={{
                  background: '#64A859',
                  animationDuration: '1.5s',
                }}
              />
            ) : (
              <CornerRightUp
                className="w-4 h-4 transition-opacity"
                style={{
                  color: inputValue.trim() ? '#101010' : '#64A859',
                  opacity: inputValue.trim() ? 1 : 0.5,
                }}
              />
            )}
          </button>
        </div>

        {/* Status line */}
        <p
          className="pl-1 mt-1.5 h-4 text-xs text-center"
          style={{ color: submitted ? '#64A859' : 'rgba(111,116,105,0.5)' }}
        >
          {submitted ? "Searching documents…" : ""}
        </p>
      </div>
    </div>
  );
}
