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
  className?: string;
};

const FloatingActionMenu = ({ options, activeLabel, className }: FloatingActionMenuProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={cn("relative", className)}>
      {/* Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 h-10 px-3 rounded-xl transition-all duration-200 border"
        style={{
          background: isOpen ? 'var(--card)' : 'rgba(32,43,33,0.6)',
          borderColor: isOpen ? 'rgba(100,168,89,0.4)' : 'rgba(111,116,105,0.25)',
          color: isOpen ? 'var(--accent)' : 'var(--muted)',
          backdropFilter: 'blur(8px)',
        }}
        onMouseEnter={e => {
          if (!isOpen) {
            (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(100,168,89,0.3)'
            ;(e.currentTarget as HTMLButtonElement).style.color = 'var(--heading)'
          }
        }}
        onMouseLeave={e => {
          if (!isOpen) {
            (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(111,116,105,0.25)'
            ;(e.currentTarget as HTMLButtonElement).style.color = 'var(--muted)'
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
            initial={{ opacity: 0, y: 8, filter: "blur(8px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            exit={{ opacity: 0, y: 8, filter: "blur(8px)" }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="absolute bottom-12 left-0 mb-1"
          >
            <div
              className="flex flex-col gap-1 p-1.5 rounded-xl"
              style={{
                background: 'var(--card)',
                border: '1px solid rgba(100,168,89,0.2)',
                boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
                backdropFilter: 'blur(12px)',
                minWidth: '160px',
              }}
            >
              {options.map((option, index) => (
                <motion.button
                  key={index}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -8 }}
                  transition={{ duration: 0.15, delay: index * 0.04 }}
                  onClick={() => { option.onClick(); setIsOpen(false) }}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-all duration-150 w-full"
                  style={{
                    background: option.active ? 'rgba(100,168,89,0.15)' : 'transparent',
                    color: option.active ? 'var(--accent)' : 'var(--muted)',
                    border: `1px solid ${option.active ? 'rgba(100,168,89,0.25)' : 'transparent'}`,
                  }}
                  onMouseEnter={e => {
                    if (!option.active) {
                      e.currentTarget.style.background = 'rgba(111,116,105,0.1)'
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
