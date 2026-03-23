import { useState, useRef, useEffect, useCallback } from 'react'
import { Zap, Globe, ChevronDown, ChevronUp, FileText, Sparkles, SquarePen, MessageSquare, Trash2, AlignLeft, BarChart2, GraduationCap, Files, Flame, Shield, CreditCard, Copy, Check } from 'lucide-react'
import FloatingActionMenu from './components/ui/floating-action-menu'
import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ShiningText } from './components/ui/shining-text'
import { cn } from './lib/utils'
import { Component as EtheralShadow } from './components/ui/etheral-shadow'
import { AIInputWithLoading } from './components/ui/ai-input-with-loading'
import { Sidebar, SidebarBody, SidebarLabel, useSidebar } from './components/ui/sidebar'

// ─── Types ────────────────────────────────────────────────────────────────────

interface Source {
  content: string
  source: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  language: 'en' | 'de'
  animated?: boolean
  query?: string
}

interface Conversation {
  id: string
  title: string
  messages: Message[]
  language: 'en' | 'de'
  createdAt: number
}

// ─── Language Config ──────────────────────────────────────────────────────────

const LANG = {
  en: {
    label: 'EN',
    placeholder: 'Ask about DEW21 Terms & Conditions…',
    heading: 'DEW21 Assistant',
    subheading: 'Instant answers from Terms & Conditions and regulatory documents',
    sourcesLabel: 'Sources',
    thinkingLabel: 'Searching documents…',
    disclaimer: 'Powered by local AI · DEW21 confidential documents',
    suggestions: [
      'What happens if I miss a payment?',
      'How long does SCHUFA store my data?',
      'How can I cancel my contract?',
      'What are the price adjustment rights?',
    ],
  },
  de: {
    label: 'DE',
    placeholder: 'Stellen Sie eine Frage zu DEW21 AGB…',
    heading: 'DEW21 Assistent',
    subheading: 'Sofortige Antworten aus AGB und regulatorischen Dokumenten',
    sourcesLabel: 'Quellen',
    thinkingLabel: 'Dokumente werden durchsucht…',
    disclaimer: 'Betrieben von lokaler KI · Vertrauliche DEW21-Dokumente',
    suggestions: [
      'Was passiert bei Zahlungsverzug?',
      'Wie lange speichert SCHUFA meine Daten?',
      'Wie kann ich den Vertrag kündigen?',
      'Was sind die Preisanpassungsrechte?',
    ],
  },
} as const

type Lang = keyof typeof LANG

type Tone = 'easy' | 'standard' | 'technical'

const TONES: Record<Lang, { value: Tone; label: string; description: string; icon: React.ReactNode }[]> = {
  en: [
    { value: 'easy',      label: 'Simplified', description: 'Plain language, no jargon',  icon: <AlignLeft className="w-3.5 h-3.5" /> },
    { value: 'standard',  label: 'Standard',   description: 'Clear and balanced',          icon: <BarChart2 className="w-3.5 h-3.5" /> },
    { value: 'technical', label: 'Expert',     description: 'Precise legal detail',        icon: <GraduationCap className="w-3.5 h-3.5" /> },
  ],
  de: [
    { value: 'easy',      label: 'Einfach',    description: 'Klare Sprache, kein Fachjargon', icon: <AlignLeft className="w-3.5 h-3.5" /> },
    { value: 'standard',  label: 'Standard',   description: 'Klar und ausgewogen',            icon: <BarChart2 className="w-3.5 h-3.5" /> },
    { value: 'technical', label: 'Experte',    description: 'Präzise rechtliche Details',     icon: <GraduationCap className="w-3.5 h-3.5" /> },
  ],
}

type DocFilter = 'all' | 'strom' | 'erdgas' | 'schufa' | 'creditreform'

const DOCS: Record<Lang, { value: DocFilter; label: string; description: string; icon: React.ReactNode }[]> = {
  en: [
    { value: 'all',          label: 'All Docs',      description: 'Search all documents',    icon: <Files className="w-3.5 h-3.5" /> },
    { value: 'strom',        label: 'Electricity',   description: 'Strom AGB',               icon: <Zap className="w-3.5 h-3.5" /> },
    { value: 'erdgas',       label: 'Gas',           description: 'Erdgas AGB',              icon: <Flame className="w-3.5 h-3.5" /> },
    { value: 'schufa',       label: 'SCHUFA',        description: 'SCHUFA appendix',         icon: <Shield className="w-3.5 h-3.5" /> },
    { value: 'creditreform', label: 'Creditreform',  description: 'Creditreform appendix',   icon: <CreditCard className="w-3.5 h-3.5" /> },
  ],
  de: [
    { value: 'all',          label: 'Alle Docs',     description: 'Alle Dokumente durchsuchen', icon: <Files className="w-3.5 h-3.5" /> },
    { value: 'strom',        label: 'Strom',         description: 'Strom AGB',                  icon: <Zap className="w-3.5 h-3.5" /> },
    { value: 'erdgas',       label: 'Erdgas',        description: 'Erdgas AGB',                 icon: <Flame className="w-3.5 h-3.5" /> },
    { value: 'schufa',       label: 'SCHUFA',        description: 'SCHUFA-Anhang',              icon: <Shield className="w-3.5 h-3.5" /> },
    { value: 'creditreform', label: 'Creditreform',  description: 'Creditreform-Anhang',        icon: <CreditCard className="w-3.5 h-3.5" /> },
  ],
}

const STORAGE_KEY = 'dew21_conversations'

// ─── Source Card ──────────────────────────────────────────────────────────────

function highlightTerms(text: string, query: string): React.ReactNode[] {
  const stopWords = new Set(['what', 'when', 'where', 'which', 'that', 'this', 'with', 'from', 'have', 'about', 'nach', 'wenn', 'dass', 'oder', 'eine', 'einer', 'wird', 'the', 'and', 'for', 'are', 'ist', 'die', 'der', 'den', 'dem', 'you', 'can', 'how', 'does', 'been'])
  const terms = query.toLowerCase().split(/\s+/).filter(w => w.length > 3 && !stopWords.has(w))
  if (terms.length === 0) return [text]
  const escaped = terms.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  const splitPattern = new RegExp(`(${escaped.join('|')})`, 'gi')
  const matchPattern = new RegExp(`^(${escaped.join('|')})$`, 'i')
  return text.split(splitPattern).map((part, i) =>
    matchPattern.test(part)
      ? <mark key={i} className="rounded px-0.5" style={{ background: 'rgba(100,168,89,0.2)', color: '#D0CFC9', fontWeight: 500 }}>{part}</mark>
      : part
  )
}

function SourceCard({ source, index, query }: { source: Source; index: number; query?: string }) {
  const name = source.source
    .replace('.pdf_en.txt', '')
    .replace('.pdf_de.txt', '')
    .replace(/_/g, ' ')

  return (
    <div className="rounded-xl p-3.5" style={{ background: '#202B21', border: '1px solid rgba(100,168,89,0.15)' }}>
      <div className="flex items-start gap-2.5">
        <div className="w-5 h-5 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5" style={{ background: 'rgba(100,168,89,0.15)', border: '1px solid rgba(100,168,89,0.25)' }}>
          <span className="text-[10px] font-mono" style={{ color: '#64A859' }}>{index + 1}</span>
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[11px] font-mono mb-1.5 truncate" style={{ color: '#64A859' }}>{name}</p>
          <p className="text-xs leading-relaxed line-clamp-3" style={{ color: '#6F7469' }}>
            {query ? highlightTerms(source.content, query) : source.content}
          </p>
        </div>
      </div>
    </div>
  )
}

// ─── Animated Markdown ────────────────────────────────────────────────────────

function AnimatedMarkdown({ content }: { content: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          strong: ({ children }) => <strong style={{ color: '#64A859', fontWeight: 600 }}>{children}</strong>,
          ul: ({ children }) => <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>,
          li: ({ children }) => <li className="leading-relaxed">{children}</li>,
          code: ({ children }) => <code className="px-1.5 py-0.5 rounded text-xs font-mono" style={{ background: 'rgba(100,168,89,0.15)', color: '#64A859' }}>{children}</code>,
          h1: ({ children }) => <h1 className="text-base font-semibold mb-2" style={{ color: '#D0CFC9' }}>{children}</h1>,
          h2: ({ children }) => <h2 className="text-sm font-semibold mb-1.5" style={{ color: '#D0CFC9' }}>{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-medium mb-1" style={{ color: '#D0CFC9' }}>{children}</h3>,
          hr: () => <hr className="my-2" style={{ borderColor: 'rgba(111,116,105,0.2)' }} />,
        }}
      >
        {content}
      </ReactMarkdown>
    </motion.div>
  )
}

// ─── Chat Message ─────────────────────────────────────────────────────────────

function ChatMessage({ message, isStreaming }: { message: Message; isStreaming?: boolean }) {
  const [sourcesOpen, setSourcesOpen] = useState(false)
  const [copied, setCopied] = useState(false)
  const isUser = message.role === 'user'
  const config = LANG[message.language]

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className={cn('flex gap-3 animate-slide-up', isUser ? 'justify-end' : 'justify-start')}>
      {!isUser && (
        <div className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 mt-1" style={{ background: 'rgba(100,168,89,0.15)', border: '1px solid rgba(100,168,89,0.25)', boxShadow: '0 0 12px rgba(100,168,89,0.1)' }}>
          <Zap className="w-4 h-4" style={{ color: '#64A859' }} />
        </div>
      )}
      <div className={cn('flex flex-col gap-2', isUser ? 'items-end max-w-[72%]' : 'items-start max-w-[80%]')}>
        <div
          className="rounded-2xl px-4 py-3 text-sm leading-relaxed"
          style={isUser
            ? { background: 'rgba(100,168,89,0.12)', border: '1px solid rgba(100,168,89,0.2)', color: '#D0CFC9', borderTopRightRadius: '4px' }
            : { background: '#202B21', border: '1px solid rgba(111,116,105,0.2)', color: '#D0CFC9', borderTopLeftRadius: '4px' }}
        >
          {isUser ? message.content : (
            <>
              {message.animated
                ? <AnimatedMarkdown content={message.content} />
                : <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                    strong: ({ children }) => <strong style={{ color: '#64A859', fontWeight: 600 }}>{children}</strong>,
                    ul: ({ children }) => <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>,
                    li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                    code: ({ children }) => <code className="px-1.5 py-0.5 rounded text-xs font-mono" style={{ background: 'rgba(100,168,89,0.15)', color: '#64A859' }}>{children}</code>,
                    h1: ({ children }) => <h1 className="text-base font-semibold mb-2" style={{ color: '#D0CFC9' }}>{children}</h1>,
                    h2: ({ children }) => <h2 className="text-sm font-semibold mb-1.5" style={{ color: '#D0CFC9' }}>{children}</h2>,
                    h3: ({ children }) => <h3 className="text-sm font-medium mb-1" style={{ color: '#D0CFC9' }}>{children}</h3>,
                    hr: () => <hr className="my-2" style={{ borderColor: 'rgba(111,116,105,0.2)' }} />,
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              }
              {isStreaming && (
                <motion.span
                  animate={{ opacity: [1, 1, 0, 0] }}
                  transition={{ duration: 0.8, repeat: Infinity, ease: 'linear', times: [0, 0.5, 0.5, 1] }}
                  className="inline-block w-0.5 h-[1em] ml-0.5 align-middle rounded-sm"
                  style={{ background: '#64A859' }}
                />
              )}
            </>
          )}
        </div>

        {/* Assistant message actions */}
        {!isUser && message.content && (
          <div className="flex items-center gap-3">
            {/* Copy button */}
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 text-xs py-0.5 transition-colors"
              style={{ color: copied ? '#64A859' : '#6F7469' }}
              onMouseEnter={e => { if (!copied) e.currentTarget.style.color = '#D0CFC9' }}
              onMouseLeave={e => { if (!copied) e.currentTarget.style.color = '#6F7469' }}
            >
              {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
              {copied ? 'Copied' : 'Copy'}
            </button>

            {/* Sources toggle */}
            {message.sources && message.sources.length > 0 && (
              <button
                onClick={() => setSourcesOpen(o => !o)}
                className="flex items-center gap-1.5 text-xs py-0.5 transition-colors"
                style={{ color: '#6F7469' }}
                onMouseEnter={e => (e.currentTarget.style.color = '#D0CFC9')}
                onMouseLeave={e => (e.currentTarget.style.color = '#6F7469')}
              >
                <FileText className="w-3 h-3" />
                {config.sourcesLabel} ({message.sources.length})
                {sourcesOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
            )}
          </div>
        )}

        {/* Source cards */}
        {!isUser && sourcesOpen && message.sources && message.sources.length > 0 && (
          <div className="flex flex-col gap-1.5 w-full animate-fade-in">
            {message.sources.map((s, i) => <SourceCard key={i} source={s} index={i} query={message.query} />)}
          </div>
        )}
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 mt-1" style={{ background: '#202B21', border: '1px solid rgba(111,116,105,0.3)' }}>
          <span className="text-xs font-semibold" style={{ color: '#6F7469' }}>U</span>
        </div>
      )}
    </div>
  )
}

// ─── Typing Indicator ─────────────────────────────────────────────────────────

function TypingIndicator({ language }: { language: Lang }) {
  return (
    <div className="flex gap-3 animate-slide-up">
      <div className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'rgba(100,168,89,0.15)', border: '1px solid rgba(100,168,89,0.25)', boxShadow: '0 0 12px rgba(100,168,89,0.1)' }}>
        <Zap className="w-4 h-4" style={{ color: '#64A859' }} />
      </div>
      <ShiningText text={LANG[language].thinkingLabel} />
    </div>
  )
}

// ─── Empty State ──────────────────────────────────────────────────────────────

function EmptyState({ language, onSuggestion }: { language: Lang; onSuggestion: (s: string) => void }) {
  const config = LANG[language]
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[55vh] gap-6 text-center animate-fade-in">
      <div className="relative">
        <div className="absolute inset-0 rounded-2xl blur-xl" style={{ background: 'rgba(100,168,89,0.2)' }} />
        <div className="relative w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(100,168,89,0.15)', border: '1px solid rgba(100,168,89,0.3)' }}>
          <Zap className="w-8 h-8" style={{ color: '#64A859' }} />
        </div>
      </div>
      <div className="space-y-1.5">
        <h2 className="font-display text-2xl font-semibold tracking-tight" style={{ color: '#D0CFC9' }}>{config.heading}</h2>
        <p className="text-sm max-w-xs" style={{ color: '#6F7469' }}>{config.subheading}</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-md">
        {config.suggestions.map(s => (
          <button key={s} onClick={() => onSuggestion(s)}
            className="flex items-start gap-2 text-left text-xs rounded-xl px-3.5 py-3 transition-all duration-200"
            style={{ background: '#202B21', border: '1px solid rgba(111,116,105,0.2)', color: '#6F7469' }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(100,168,89,0.3)'; e.currentTarget.style.color = '#D0CFC9' }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(111,116,105,0.2)'; e.currentTarget.style.color = '#6F7469' }}
          >
            <Sparkles className="w-3 h-3 mt-0.5 flex-shrink-0" style={{ color: '#64A859', opacity: 0.6 }} />
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}

// ─── Language Toggle ──────────────────────────────────────────────────────────

function LanguageToggle({ language, onChange }: { language: Lang; onChange: (l: Lang) => void }) {
  return (
    <div className="flex items-center gap-1 rounded-lg p-1" style={{ background: '#202B21', border: '1px solid rgba(111,116,105,0.25)' }}>
      <Globe className="w-3.5 h-3.5 ml-1.5" style={{ color: '#6F7469' }} />
      {(['en', 'de'] as Lang[]).map(lang => (
        <button key={lang} onClick={() => onChange(lang)}
          className="px-3 py-1 rounded-md text-xs font-medium transition-all duration-200"
          style={language === lang ? { background: '#64A859', color: '#101010', fontWeight: 600 } : { color: '#6F7469' }}
          onMouseEnter={e => { if (language !== lang) e.currentTarget.style.color = '#D0CFC9' }}
          onMouseLeave={e => { if (language !== lang) e.currentTarget.style.color = '#6F7469' }}
        >
          {LANG[lang].label}
        </button>
      ))}
    </div>
  )
}

// ─── Sidebar Content ──────────────────────────────────────────────────────────

function SidebarContent({ conversations, activeId, onSelect, onNew, onDelete }: {
  conversations: Conversation[]
  activeId: string | null
  onSelect: (c: Conversation) => void
  onNew: () => void
  onDelete: (id: string) => void
}) {
  const { open } = useSidebar()

  const formatDate = (ts: number) => {
    const diff = Date.now() - ts
    if (diff < 86400000) return 'Today'
    if (diff < 172800000) return 'Yesterday'
    return new Date(ts).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' })
  }

  return (
    <div className="flex flex-col h-full gap-3">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-1 py-1 flex-shrink-0">
        <div className="relative flex-shrink-0">
          <div className="absolute inset-0 rounded-lg blur-md" style={{ background: 'rgba(100,168,89,0.25)' }} />
          <div className="relative w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: '#64A859' }}>
            <Zap className="w-4 h-4" style={{ color: '#101010' }} />
          </div>
        </div>
        <motion.span
          animate={{ opacity: open ? 1 : 0 }}
          transition={{ duration: 0.15 }}
          className="font-display text-sm font-semibold tracking-tight whitespace-nowrap"
          style={{ color: '#D0CFC9' }}
        >
          DEW21
        </motion.span>
      </div>

      {/* New Chat */}
      <button onClick={onNew}
        className="flex items-center gap-2.5 px-2 py-2 rounded-xl transition-all duration-200 flex-shrink-0"
        style={{ background: 'rgba(100,168,89,0.1)', border: '1px solid rgba(100,168,89,0.2)' }}
        onMouseEnter={e => (e.currentTarget.style.background = 'rgba(100,168,89,0.2)')}
        onMouseLeave={e => (e.currentTarget.style.background = 'rgba(100,168,89,0.1)')}
      >
        <SquarePen className="w-4 h-4 flex-shrink-0" style={{ color: '#64A859' }} />
        <SidebarLabel style={{ color: '#64A859' }}>New Chat</SidebarLabel>
      </button>

      <div className="flex-shrink-0" style={{ height: '1px', background: 'rgba(111,116,105,0.15)' }} />

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto space-y-1 min-h-0">
        {conversations.length === 0 ? (
          <motion.p
            animate={{ opacity: open ? 1 : 0 }}
            transition={{ duration: 0.15 }}
            className="text-xs px-2 py-3 text-center whitespace-nowrap" style={{ color: '#6F7469' }}>
            No conversations yet
          </motion.p>
        ) : (
          conversations.slice().sort((a, b) => b.createdAt - a.createdAt).map(conv => (
            <div key={conv.id}
              className="group flex items-center gap-2 px-2 py-2 rounded-xl cursor-pointer transition-all duration-150"
              style={{
                background: activeId === conv.id ? 'rgba(100,168,89,0.15)' : 'transparent',
                border: `1px solid ${activeId === conv.id ? 'rgba(100,168,89,0.25)' : 'transparent'}`,
              }}
              onClick={() => onSelect(conv)}
              onMouseEnter={e => { if (activeId !== conv.id) e.currentTarget.style.background = 'rgba(111,116,105,0.1)' }}
              onMouseLeave={e => { if (activeId !== conv.id) e.currentTarget.style.background = 'transparent' }}
            >
              <MessageSquare className="w-4 h-4 flex-shrink-0" style={{ color: activeId === conv.id ? '#64A859' : '#6F7469' }} />
              <motion.div
                animate={{ opacity: open ? 1 : 0 }}
                transition={{ duration: 0.15 }}
                className="flex-1 min-w-0 flex flex-col"
              >
                <span className="text-xs truncate whitespace-nowrap" style={{ color: activeId === conv.id ? '#D0CFC9' : '#6F7469' }}>{conv.title}</span>
                <span className="text-[10px] whitespace-nowrap" style={{ color: 'rgba(111,116,105,0.6)' }}>
                  {formatDate(conv.createdAt)} · {conv.language.toUpperCase()}
                </span>
              </motion.div>
              <motion.button
                animate={{ opacity: open ? 1 : 0 }}
                transition={{ duration: 0.15 }}
                onClick={e => { e.stopPropagation(); onDelete(conv.id) }}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 rounded flex-shrink-0"
                style={{ color: '#6F7469' }}
                onMouseEnter={e => (e.currentTarget.style.color = '#ef4444')}
                onMouseLeave={e => (e.currentTarget.style.color = '#6F7469')}
              >
                <Trash2 className="w-3 h-3" />
              </motion.button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

// ─── App ──────────────────────────────────────────────────────────────────────

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [language, setLanguage] = useState<Lang>('de')
  const [tone, setTone] = useState<Tone>('standard')
  const [docFilter, setDocFilter] = useState<DocFilter>('all')
  const [loading, setLoading] = useState(false)
  const [streamingId, setStreamingId] = useState<string | null>(null)
  const [conversations, setConversations] = useState<Conversation[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      return saved ? JSON.parse(saved) : []
    } catch {
      return []
    }
  })
  const [activeId, setActiveId] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const currentIdRef = useRef<string | null>(null)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations))
  }, [conversations])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const saveMessages = useCallback((msgs: Message[], lang: Lang) => {
    if (msgs.length === 0) return
    const id = currentIdRef.current ?? (() => {
      const newId = Date.now().toString()
      currentIdRef.current = newId
      setActiveId(newId)
      return newId
    })()
    setConversations(prev => {
      const existing = prev.find(c => c.id === id)
      if (existing) return prev.map(c => c.id === id ? { ...c, messages: msgs, language: lang } : c)
      return [...prev, {
        id,
        title: msgs[0]?.content.slice(0, 45) + (msgs[0]?.content.length > 45 ? '…' : '') || 'New Chat',
        messages: msgs,
        language: lang,
        createdAt: Date.now(),
      }]
    })
  }, [])

  const generateTitle = useCallback(async (query: string, lang: Lang, convId: string) => {
    try {
      const res = await fetch('/api/title', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, language: lang }),
      })
      const data = await res.json()
      if (data.title) {
        setConversations(prev => prev.map(c => c.id === convId ? { ...c, title: data.title } : c))
      }
    } catch {
      // silently fail
    }
  }, [])

  const handleSubmit = useCallback(async (query: string) => {
    if (!query.trim() || loading) return

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: query.trim(), language }
    const updatedMsgs = [...messages, userMsg]
    setMessages(updatedMsgs)
    setLoading(true)

    const isNewConversation = currentIdRef.current === null
    const history = messages.slice(-6).map(m => ({ role: m.role, content: m.content }))
    const assistantId = (Date.now() + 1).toString()
    let fullContent = ''
    let finalSources: Source[] | undefined

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, language, tone, document: docFilter, history }),
      })

      if (!res.body) throw new Error('No stream')

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let assistantAdded = false

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n\n')
        buffer = parts.pop() ?? ''

        for (const part of parts) {
          if (!part.startsWith('data: ')) continue
          const event = JSON.parse(part.slice(6))

          if (event.type === 'sources') {
            finalSources = event.sources
          } else if (event.type === 'token') {
            fullContent += event.token
            if (!assistantAdded) {
              setLoading(false)
              setStreamingId(assistantId)
              setMessages([...updatedMsgs, {
                id: assistantId, role: 'assistant', content: fullContent, sources: finalSources, language, animated: true, query: query.trim(),
              }])
              assistantAdded = true
            } else {
              setMessages(prev => prev.map(m =>
                m.id === assistantId ? { ...m, content: fullContent } : m
              ))
            }
          } else if (event.type === 'done') {
            setStreamingId(null)
            const finalMsg: Message = {
              id: assistantId, role: 'assistant', content: fullContent, sources: finalSources, language, query: query.trim(),
            }
            saveMessages([...updatedMsgs, finalMsg], language)
            if (isNewConversation && currentIdRef.current) {
              generateTitle(query, language, currentIdRef.current)
            }
          }
        }
      }

      if (!assistantAdded) setLoading(false)
    } catch {
      const errMsg: Message = {
        id: assistantId, role: 'assistant',
        content: language === 'de'
          ? 'Fehler beim Abrufen der Antwort. Ist der Server erreichbar?'
          : 'Error fetching response. Is the server running?',
        language,
      }
      setMessages([...updatedMsgs, errMsg])
      saveMessages([...updatedMsgs, errMsg], language)
      setLoading(false)
    }
  }, [messages, language, tone, docFilter, loading, saveMessages, generateTitle])

  const startNewChat = () => {
    setMessages([])
    setActiveId(null)
    currentIdRef.current = null
    setSidebarOpen(false)
  }

  const loadConversation = (conv: Conversation) => {
    setMessages(conv.messages)
    setActiveId(conv.id)
    currentIdRef.current = conv.id
    setLanguage(conv.language)
    setSidebarOpen(false)
  }

  const deleteConversation = (id: string) => {
    setConversations(prev => prev.filter(c => c.id !== id))
    if (activeId === id) startNewChat()
  }

  return (
    <div className="h-screen flex flex-col font-sans relative overflow-hidden" style={{ background: '#101010' }}>
      {/* Background */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <EtheralShadow color="rgba(100, 168, 89, 0.35)" animation={{ scale: 60, speed: 70 }} noise={{ opacity: 0.4, scale: 1.2 }} sizing="fill" />
        <div className="absolute inset-0" style={{ background: 'rgba(16,16,16,0.55)' }} />
      </div>

      {/* Layout */}
      <div className="relative z-10 flex h-full overflow-hidden">

        {/* Sidebar */}
        <Sidebar open={sidebarOpen} setOpen={setSidebarOpen}>
          <SidebarBody className="h-full" style={{ background: 'rgba(13,26,14,0.95)', borderRight: '1px solid rgba(100,168,89,0.12)' }}>
            <SidebarContent conversations={conversations} activeId={activeId} onSelect={loadConversation} onNew={startNewChat} onDelete={deleteConversation} />
          </SidebarBody>
        </Sidebar>

        {/* Main */}
        <div className="flex flex-col flex-1 min-w-0">

          {/* Header */}
          <header className="px-6 py-3.5 flex items-center justify-between flex-shrink-0 backdrop-blur-md"
            style={{ borderBottom: '1px solid rgba(111,116,105,0.15)', background: 'rgba(16,16,16,0.8)' }}>
            <div className="flex items-center gap-2">
              <span className="font-display text-sm font-semibold tracking-tight" style={{ color: '#D0CFC9' }}>DEW21</span>
              <span className="text-sm hidden sm:inline" style={{ color: '#6F7469' }}>Document Assistant</span>
            </div>
            <LanguageToggle language={language} onChange={setLanguage} />
          </header>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto">
            <div className="max-w-2xl mx-auto px-4 py-8">
              {messages.length === 0
                ? <EmptyState language={language} onSuggestion={s => handleSubmit(s)} />
                : (
                  <div className="flex flex-col gap-6">
                    {messages.map(m => <ChatMessage key={m.id} message={m} isStreaming={m.id === streamingId} />)}
                    {loading && <TypingIndicator language={language} />}
                    <div ref={bottomRef} />
                  </div>
                )}
            </div>
          </div>

          {/* Input */}
          <div className="px-4 py-4 backdrop-blur-md flex-shrink-0"
            style={{ borderTop: '1px solid rgba(111,116,105,0.15)', background: 'rgba(16,16,16,0.8)' }}>
            <div className="max-w-2xl mx-auto">
              <AIInputWithLoading
                placeholder={LANG[language].placeholder}
                onSubmit={handleSubmit}
                loadingDuration={0}
                toolbar={
                  <div className="flex items-center gap-1.5">
                    <FloatingActionMenu
                      activeLabel={TONES[language].find(t => t.value === tone)?.label}
                      options={TONES[language].map(t => ({
                        label: t.label, sublabel: t.description, active: tone === t.value,
                        Icon: t.icon, onClick: () => setTone(t.value),
                      }))}
                    />
                    <FloatingActionMenu
                      activeLabel={DOCS[language].find(d => d.value === docFilter)?.label}
                      isActive={docFilter !== 'all'}
                      options={DOCS[language].map(d => ({
                        label: d.label, sublabel: d.description, active: docFilter === d.value,
                        Icon: d.icon, onClick: () => setDocFilter(d.value),
                      }))}
                    />
                  </div>
                }
              />
              <p className="text-center text-[11px] mt-2" style={{ color: 'rgba(111,116,105,0.4)' }}>
                {LANG[language].disclaimer}
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
