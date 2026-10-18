import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Copy,
  Check,
  BookOpen,
  Menu,
  ShieldAlert,
  PanelLeft,
  PanelLeftClose,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message, User, MentionItem } from '../types';
import { MentionMenu } from './MentionMenu';

interface ChatAreaProps {
  messages: Message[];
  onSendMessage: (text: string) => Promise<void>;
  isGenerating: boolean;
  onStopGenerating?: () => void;
  user: User | null;
  onOpenMobileSidebar: () => void;
  availableMentions: MentionItem[];
  onTriggerMentionWorkflow: (workflow: string, key: string) => void;
  conversationTitle?: string;
  isDesktopSidebarCollapsed?: boolean;
  onToggleDesktopSidebar?: () => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  onSendMessage,
  isGenerating,
  user,
  onOpenMobileSidebar,
  availableMentions,
  onTriggerMentionWorkflow,
  conversationTitle,
  isDesktopSidebarCollapsed,
  onToggleDesktopSidebar,
}) => {
  const [inputText, setInputText] = useState('');
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  // Mention State
  const [showMentionMenu, setShowMentionMenu] = useState(false);
  const [mentionQuery, setMentionQuery] = useState('');
  const [selectedMentionIndex, setSelectedMentionIndex] = useState(0);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isGenerating]);

  // Adjust textarea height automatically
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [inputText]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setInputText(val);

    // Check for @ mention trigger
    const lastAtIndex = val.lastIndexOf('@');
    if (lastAtIndex !== -1 && (lastAtIndex === 0 || val[lastAtIndex - 1] === ' ')) {
      const query = val.slice(lastAtIndex + 1);
      if (!query.includes(' ')) {
        setShowMentionMenu(true);
        setMentionQuery(query);
        setSelectedMentionIndex(0);
        return;
      }
    }
    setShowMentionMenu(false);
  };

  const filteredMentions = availableMentions.filter(
    (m) =>
      m.label.toLowerCase().includes(mentionQuery.toLowerCase()) ||
      m.key.toLowerCase().includes(mentionQuery.toLowerCase())
  );

  const handleSelectMention = (item: MentionItem) => {
    const lastAtIndex = inputText.lastIndexOf('@');
    if (lastAtIndex !== -1) {
      const before = inputText.slice(0, lastAtIndex);
      const newText = `${before}${item.label} `;
      setInputText(newText);
    }
    setShowMentionMenu(false);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }

    if (item.workflow === 'principal_elevation' || item.workflow === 'student_records') {
      onTriggerMentionWorkflow(item.workflow, item.key);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (showMentionMenu && filteredMentions.length > 0) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedMentionIndex((prev) => (prev + 1) % filteredMentions.length);
        return;
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedMentionIndex((prev) => (prev - 1 + filteredMentions.length) % filteredMentions.length);
        return;
      }
      if (e.key === 'Enter' || e.key === 'Tab') {
        e.preventDefault();
        handleSelectMention(filteredMentions[selectedMentionIndex]);
        return;
      }
      if (e.key === 'Escape') {
        setShowMentionMenu(false);
        return;
      }
    }

    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = async () => {
    const trimmed = inputText.trim();
    if (!trimmed || isGenerating) return;

    if (trimmed.startsWith('@principal')) {
      onTriggerMentionWorkflow('principal_elevation', 'principal');
    }

    const studentMatch = trimmed.match(/^@([A-Za-z0-9_]+)/);
    if (studentMatch) {
      const handle = studentMatch[1];
      if (handle.toLowerCase() === 'student' || handle === user?.username) {
        onTriggerMentionWorkflow('student_records', handle);
      }
    }

    setInputText('');
    setShowMentionMenu(false);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    await onSendMessage(trimmed);
  };

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const suggestions = [
    'Find the current academic regulations',
    'Explain the course registration process',
    'Where can I find institutional guidelines?',
    'What campus information is available to my account?',
  ];

  return (
    <div className="flex flex-1 flex-col h-screen overflow-hidden bg-[#F7F7F5] dark:bg-[#151515]">
      {/* Top Application Header */}
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-[#E6E5E1] bg-[#FFFFFF] px-4 dark:border-[#343434] dark:bg-[#1D1D1D]">
        <div className="flex items-center gap-2">
          {/* Mobile Menu Button */}
          <button
            onClick={onOpenMobileSidebar}
            className="rounded p-1.5 text-[#686868] hover:bg-[#F0F0ED] hover:text-[#1C1C1C] dark:hover:bg-[#252525] dark:hover:text-[#F3F3F3] lg:hidden"
            aria-label="Open sidebar"
          >
            <Menu className="h-4 w-4" />
          </button>

          {/* Desktop Sidebar Toggle Button */}
          {onToggleDesktopSidebar && (
            <button
              onClick={onToggleDesktopSidebar}
              className="hidden lg:flex rounded p-1.5 text-[#686868] hover:bg-[#F0F0ED] hover:text-[#1C1C1C] dark:hover:bg-[#252525] dark:hover:text-[#F3F3F3]"
              title={isDesktopSidebarCollapsed ? 'Open sidebar' : 'Collapse sidebar'}
              aria-label={isDesktopSidebarCollapsed ? 'Open sidebar' : 'Collapse sidebar'}
            >
              {isDesktopSidebarCollapsed ? (
                <PanelLeft className="h-4 w-4" />
              ) : (
                <PanelLeftClose className="h-4 w-4" />
              )}
            </button>
          )}

          <div className="ml-1">
            <h2 className="text-xs font-semibold text-[#1C1C1C] dark:text-[#F3F3F3] truncate max-w-xs sm:max-w-md">
              {conversationTitle || 'CampusMind'}
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-2 text-right">
          <span className="text-[11px] text-[#686868] dark:text-[#B5B5B5] hidden sm:inline">
            Role: <span className="font-medium text-[#1C1C1C] dark:text-[#F3F3F3] capitalize">{user?.role || 'Guest'}</span>
          </span>
          <span className="rounded border border-[#E6E5E1] bg-[#F7F7F5] px-1.5 py-0.5 text-[10px] text-[#686868] dark:border-[#343434] dark:bg-[#252525] dark:text-[#B5B5B5]">
            Claude 3.5 Sonnet
          </span>
        </div>
      </header>

      {/* Main Messages & Welcome Viewport */}
      <div className="flex-1 overflow-y-auto px-4 py-8">
        <div className="mx-auto max-w-2xl space-y-6">
          {messages.length === 0 ? (
            /* Luxury Minimalist Editorial Welcome Screen */
            <div className="pt-8 sm:pt-14 pb-4 text-center">
              <h1 className="font-editorial text-3xl sm:text-4xl md:text-5xl lg:text-[46px] font-normal tracking-tight text-[#1C1C1C] dark:text-[#F3F3F3] leading-[1.18] max-w-xl mx-auto">
                Complex campus information, made simple.
              </h1>
              <p className="mx-auto mt-3 max-w-md text-xs sm:text-sm text-[#686868] dark:text-[#B5B5B5] leading-relaxed">
                Find reliable answers from authorized institutional documents and academic information.
              </p>

              {/* Centered Composer for Welcome Screen */}
              <div className="mt-8 sm:mt-10 max-w-xl mx-auto relative">
                {/* Autocomplete Mention Menu */}
                {showMentionMenu && (
                  <MentionMenu
                    mentions={filteredMentions}
                    selectedIndex={selectedMentionIndex}
                    onSelect={handleSelectMention}
                    position={{ top: 0, left: 0 }}
                  />
                )}

                {/* Wide Rounded Composer */}
                <div className="relative rounded-3xl border border-[#E6E5E1] bg-[#FFFFFF] shadow-[0_4px_24px_rgba(0,0,0,0.03)] transition-all focus-within:border-[#7D91C9] focus-within:ring-2 focus-within:ring-[#7D91C9]/20 dark:border-[#343434] dark:bg-[#1D1D1D] dark:shadow-[0_4px_24px_rgba(0,0,0,0.25)] dark:focus-within:border-[#9EAFE8]">
                  <textarea
                    ref={textareaRef}
                    rows={2}
                    value={inputText}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask anything about campus policies, courses, or identity records…"
                    className="w-full resize-none bg-transparent px-5 pt-4 pb-2 text-xs sm:text-sm text-[#1C1C1C] placeholder-[#898989] focus:outline-none dark:text-[#F3F3F3] dark:placeholder-[#929292] min-h-[52px]"
                  />

                  <div className="flex items-center justify-between px-4 pb-3 pt-1 border-t border-transparent">
                    <div className="text-[11px] text-[#898989] dark:text-[#929292]">
                      Enter to send · Shift+Enter for newline
                    </div>

                    <button
                      onClick={handleSend}
                      disabled={!inputText.trim() || isGenerating}
                      className="flex h-8 w-8 items-center justify-center rounded-full bg-[#171717] text-[#FFFFFF] transition-colors hover:bg-[#2A2A2A] disabled:opacity-30 disabled:hover:bg-[#171717] dark:bg-[#F1F1F1] dark:text-[#181818] dark:hover:bg-[#E5E5E5] cursor-pointer"
                      title="Send message"
                      aria-label="Send message"
                    >
                      <Send className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>

                {/* Suggested Questions below Composer */}
                <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
                  {suggestions.map((question, i) => (
                    <button
                      key={i}
                      onClick={() => onSendMessage(question)}
                      className="rounded-full border border-[#E6E5E1] bg-[#FFFFFF] px-3.5 py-1.5 text-xs text-[#1C1C1C] transition-colors hover:border-[#171717] hover:bg-[#F0F0ED] dark:border-[#343434] dark:bg-[#1D1D1D] dark:text-[#F3F3F3] dark:hover:border-[#F1F1F1] dark:hover:bg-[#252525] text-left"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Active Conversation Layout */
            messages.map((msg, idx) => {
              const isUser = msg.role === 'user';
              return (
                <div
                  key={idx}
                  className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} space-y-1`}
                >
                  <span className="text-[10px] font-medium tracking-normal text-[#686868] dark:text-[#B5B5B5] px-1">
                    {isUser ? user?.full_name || 'You' : 'CampusMind'}
                  </span>

                  <div
                    className={`max-w-full rounded-2xl px-4 py-3 text-xs leading-relaxed ${
                      isUser
                        ? 'bg-[#171717] text-white dark:bg-[#F1F1F1] dark:text-[#181818]'
                        : 'border border-[#E6E5E1] bg-[#FFFFFF] text-[#1C1C1C] dark:border-[#343434] dark:bg-[#1D1D1D] dark:text-[#F3F3F3]'
                    }`}
                  >
                    <div
                      className={`prose prose-xs max-w-none prose-p:leading-relaxed ${
                        isUser
                          ? 'prose-invert text-white dark:text-[#181818]'
                          : 'dark:prose-invert text-[#1C1C1C] dark:text-[#F3F3F3]'
                      }`}
                    >
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>

                    {/* Insufficient Evidence Notice */}
                    {msg.insufficient_evidence && (
                      <div className="mt-3 flex items-start gap-2 rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] p-2.5 text-[11px] text-[#686868] dark:border-[#343434] dark:bg-[#252525] dark:text-[#B5B5B5]">
                        <ShieldAlert className="h-4 w-4 shrink-0 mt-0.5" />
                        <span>
                          Notice: No authorized campus documents matched this query with sufficient evidence. Hallucination was safely prevented.
                        </span>
                      </div>
                    )}

                    {/* Citations */}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-3 pt-2.5 border-t border-[#E6E5E1] dark:border-[#343434]">
                        <span className="text-[10px] font-medium uppercase tracking-wider text-[#686868] dark:text-[#B5B5B5] block mb-1.5 flex items-center gap-1">
                          <BookOpen className="h-3 w-3" /> Sources ({msg.citations.length})
                        </span>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {msg.citations.map((c, cIdx) => (
                            <div
                              key={cIdx}
                              className="rounded border border-[#E6E5E1] bg-[#F7F7F5] p-2 text-[11px] dark:border-[#343434] dark:bg-[#252525]"
                            >
                              <div className="font-medium text-[#1C1C1C] dark:text-[#F3F3F3] truncate">
                                {c.document_title}
                              </div>
                              <div className="mt-1 flex items-center justify-between text-[10px] text-[#686868] dark:text-[#B5B5B5]">
                                <span>{c.section_heading || 'Section'}</span>
                                {c.similarity_score && (
                                  <span className="font-mono">
                                    {(c.similarity_score * 100).toFixed(0)}% match
                                  </span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {!isUser && (
                    <div className="flex items-center gap-2 px-1">
                      <button
                        onClick={() => handleCopy(msg.content, idx)}
                        className="flex items-center gap-1 text-[11px] text-[#686868] hover:text-[#1C1C1C] dark:text-[#B5B5B5] dark:hover:text-[#F3F3F3]"
                        title="Copy message"
                      >
                        {copiedIndex === idx ? (
                          <>
                            <Check className="h-3 w-3" />
                            <span>Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="h-3 w-3" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              );
            })
          )}

          {/* Generating Indicator */}
          {isGenerating && (
            <div className="flex flex-col items-start space-y-1">
              <span className="text-[10px] font-medium text-[#686868] dark:text-[#B5B5B5] px-1">
                CampusMind
              </span>
              <div className="rounded-2xl border border-[#E6E5E1] bg-[#FFFFFF] px-4 py-3 dark:border-[#343434] dark:bg-[#1D1D1D]">
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-[#171717] animate-pulse dark:bg-[#F1F1F1]" />
                  <div className="h-1.5 w-1.5 rounded-full bg-[#171717] animate-pulse delay-150 dark:bg-[#F1F1F1]" />
                  <div className="h-1.5 w-1.5 rounded-full bg-[#171717] animate-pulse delay-300 dark:bg-[#F1F1F1]" />
                  <span className="ml-1 text-xs text-[#686868] dark:text-[#B5B5B5]">
                    Searching verified institutional knowledge...
                  </span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Persistent Bottom Composer when conversation is active */}
      {messages.length > 0 && (
        <footer className="border-t border-[#E6E5E1] bg-[#FFFFFF] p-4 dark:border-[#343434] dark:bg-[#1D1D1D]">
          <div className="mx-auto max-w-2xl relative">
            {showMentionMenu && (
              <MentionMenu
                mentions={filteredMentions}
                selectedIndex={selectedMentionIndex}
                onSelect={handleSelectMention}
                position={{ top: 0, left: 0 }}
              />
            )}

            <div className="relative rounded-2xl border border-[#E6E5E1] bg-[#FFFFFF] transition-colors focus-within:border-[#7D91C9] dark:border-[#343434] dark:bg-[#1D1D1D] dark:focus-within:border-[#9EAFE8]">
              <textarea
                ref={textareaRef}
                rows={1}
                value={inputText}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything about campus policies or type @ for commands…"
                className="w-full resize-none bg-transparent px-4 py-3 text-xs text-[#1C1C1C] placeholder-[#898989] focus:outline-none dark:text-[#F3F3F3] dark:placeholder-[#929292] min-h-[44px]"
              />

              <div className="flex items-center justify-between border-t border-[#E6E5E1]/40 px-3 py-2 dark:border-[#343434]/40">
                <div className="text-[11px] text-[#898989] dark:text-[#929292]">
                  Enter to send · Shift+Enter for newline
                </div>

                <button
                  onClick={handleSend}
                  disabled={!inputText.trim() || isGenerating}
                  className="flex h-7 w-7 items-center justify-center rounded-full bg-[#171717] text-white transition-colors hover:bg-[#2A2A2A] disabled:opacity-30 disabled:hover:bg-[#171717] dark:bg-[#F1F1F1] dark:text-[#181818] cursor-pointer"
                  title="Send message"
                  aria-label="Send message"
                >
                  <Send className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>
        </footer>
      )}
    </div>
  );
};
