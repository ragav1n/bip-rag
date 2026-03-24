"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { SlidersHorizontal, X } from "lucide-react";
import { cn } from "@/lib/utils";

type FloatingActionMenuProps = {
  options: {
    label: string;
    sublabel?: string;
    onClick: () => void;
    active?: boolean;
    Icon?: React.ReactNode;
  }[];
  activeLabel?: string;
  isActive?: boolean;
  className?: string;
};

const FloatingActionMenu = ({ options, activeLabel, isActive, className }: FloatingActionMenuProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={cn("relative", className)}>
      {/* Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 h-10 px-3 rounded-xl transition-all duration-200 border"
        style={{
          background: isOpen ? 'rgba(255,255,255,0.14)' : isActive ? 'rgba(245,107,0,0.15)' : 'rgba(255,255,255,0.08)',
          borderColor: isOpen ? 'rgba(255,255,255,0.3)' : isActive ? 'rgba(245,107,0,0.5)' : 'rgba(255,255,255,0.15)',
          boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.1)',
          color: isOpen ? 'var(--accent)' : isActive ? '#F56B00' : 'var(--muted)',
          backdropFilter: 'blur(8px)',
        }}
        onMouseEnter={e => {
          if (!isOpen) {
            (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(245,107,0,0.3)'
            ;(e.currentTarget as HTMLButtonElement).style.color = 'var(--heading)'
          }
        }}
        onMouseLeave={e => {
          if (!isOpen) {
            (e.currentTarget as HTMLButtonElement).style.borderColor = isActive ? 'rgba(245,107,0,0.5)' : 'rgba(245,107,0,0.28)'
            ;(e.currentTarget as HTMLButtonElement).style.color = isActive ? '#F56B00' : 'var(--muted)'
          }
        }}
      >
        <motion.div
          animate={{ rotate: isOpen ? 90 : 0 }}
          transition={{ duration: 0.25, ease: "easeInOut" }}
        >
          {isOpen ? <X className="w-3.5 h-3.5" /> : <SlidersHorizontal className="w-3.5 h-3.5" />}
        </motion.div>
        <span className="text-xs font-medium whitespace-nowrap">
          {activeLabel ?? 'Tone'}
        </span>
      </button>

      {/* Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 6 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="absolute bottom-12 left-0 mb-1"
          >
            <div
              className="flex flex-col gap-1 p-1.5 rounded-xl"
              style={{
                background: 'rgba(18,18,18,0.92)',
                border: '1px solid rgba(255,255,255,0.15)',
                boxShadow: '0 16px 48px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08)',
                backdropFilter: 'blur(20px)',
                minWidth: '160px',
              }}
            >
              {options.map((option, i) => (
                <motion.button
                  key={option.label}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.1, delay: i * 0.03 }}
                  onClick={() => { option.onClick(); setIsOpen(false) }}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-all duration-150 w-full"
                  style={{
                    background: option.active ? 'rgba(245,107,0,0.15)' : 'transparent',
                    color: option.active ? 'var(--accent)' : 'var(--muted)',
                    border: `1px solid ${option.active ? 'rgba(245,107,0,0.25)' : 'transparent'}`,
                  }}
                  onMouseEnter={e => {
                    if (!option.active) {
                      e.currentTarget.style.background = 'rgba(255,255,255,0.1)'
                      e.currentTarget.style.color = 'var(--heading)'
                    }
                  }}
                  onMouseLeave={e => {
                    if (!option.active) {
                      e.currentTarget.style.background = 'transparent'
                      e.currentTarget.style.color = 'var(--muted)'
                    }
                  }}
                >
                  {option.Icon && (
                    <span className="flex-shrink-0">{option.Icon}</span>
                  )}
                  <div className="flex flex-col">
                    <span className="text-xs font-medium">{option.label}</span>
                    {option.sublabel && (
                      <span className="text-[10px] opacity-60 mt-0.5">{option.sublabel}</span>
                    )}
                  </div>
                  {option.active && (
                    <div className="ml-auto w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: 'var(--accent)' }} />
                  )}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FloatingActionMenu;
