import { useState, useRef, useEffect, useCallback } from 'react'
import { Zap, Globe, ChevronDown, ChevronUp, FileText, Sparkles, SquarePen, MessageSquare, Trash2, AlignLeft, BarChart2, GraduationCap } from 'lucide-react'
import FloatingActionMenu from './components/ui/floating-action-menu'
import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { MessageLoading } from './components/ui/message-loading'
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

const TONES: { value: Tone; label: string; description: string; icon: React.ReactNode }[] = [
  { value: 'easy',      label: 'Simplified', description: 'Plain language, no jargon',  icon: <AlignLeft className="w-3.5 h-3.5" /> },
  { value: 'standard',  label: 'Standard',   description: 'Clear and balanced',          icon: <BarChart2 className="w-3.5 h-3.5" /> },
  { value: 'technical', label: 'Expert',     description: 'Precise legal detail',        icon: <GraduationCap className="w-3.5 h-3.5" /> },
]

const STORAGE_KEY = 'dew21_conversations'

// ─── Source Card ──────────────────────────────────────────────────────────────

function SourceCard({ source, index }: { source: Source; index: number }) {
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
          <p className="text-xs leading-relaxed line-clamp-3" style={{ color: '#6F7469' }}>{source.content}</p>
        </div>
      </div>
    </div>
  )
}

// ─── Chat Message ─────────────────────────────────────────────────────────────

function ChatMessage({ message }: { message: Message }) {
  const [sourcesOpen, setSourcesOpen] = useState(false)
  const isUser = message.role === 'user'
  const config = LANG[message.language]

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
              {message.content}
            </ReactMarkdown>
          )}
        </div>
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="w-full">
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
            {sourcesOpen && (
              <div className="flex flex-col gap-1.5 mt-2 animate-fade-in">
                {message.sources.map((s, i) => <SourceCard key={i} source={s} index={i} />)}
              </div>
            )}
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
      <div className="rounded-2xl px-4 py-3 flex items-center gap-2" style={{ background: '#202B21', border: '1px solid rgba(111,116,105,0.2)', borderTopLeftRadius: '4px', color: '#64A859' }}>
        <MessageLoading />
        <span className="text-xs" style={{ color: '#6F7469' }}>{LANG[language].thinkingLabel}</span>
      </div>
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
  const [loading, setLoading] = useState(false)
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

  // Persist to localStorage on every change
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
      // silently fail — title stays as truncated query
    }
  }, [])

  const handleSubmit = useCallback(async (query: string) => {
    if (!query.trim() || loading) return
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: query.trim(), language }
    const updatedMsgs = [...messages, userMsg]
    setMessages(updatedMsgs)
    setLoading(true)
    const isNewConversation = currentIdRef.current === null
    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, language, tone }),
      })
      const data = await res.json()
      const assistantMsg: Message = { id: (Date.now() + 1).toString(), role: 'assistant', content: data.answer, sources: data.sources, language }
      const final = [...updatedMsgs, assistantMsg]
      setMessages(final)
      saveMessages(final, language)
      if (isNewConversation && currentIdRef.current) {
        generateTitle(query, language, currentIdRef.current)
      }
    } catch {
      const errMsg: Message = {
        id: (Date.now() + 1).toString(), role: 'assistant',
        content: language === 'de' ? 'Fehler beim Abrufen der Antwort. Ist der Server erreichbar?' : 'Error fetching response. Is the server running?',
        language,
      }
      const final = [...updatedMsgs, errMsg]
      setMessages(final)
      saveMessages(final, language)
    } finally {
      setLoading(false)
    }
  }, [messages, language, tone, loading, saveMessages, generateTitle])

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
        <div className="absolute inset-0" style={{ background: 'rgba(16,16,16,0.82)' }} />
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
                    {messages.map(m => <ChatMessage key={m.id} message={m} />)}
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
                  <FloatingActionMenu
                    activeLabel={TONES.find(t => t.value === tone)?.label}
                    options={TONES.map(t => ({
                      label: t.label,
                      sublabel: t.description,
                      active: tone === t.value,
                      Icon: t.icon,
                      onClick: () => setTone(t.value),
                    }))}
                  />
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
