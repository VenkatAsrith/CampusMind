import { useState, useEffect } from 'react';
import { api } from './lib/api-client';
import type { User, ConversationSummary, Message, MentionItem, StudentRecord } from './types';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { AdminKnowledgeStudio } from './components/AdminKnowledgeStudio';
import { LoginModal } from './components/LoginModal';
import { PrincipalAuthModal } from './components/PrincipalAuthModal';
import { StudentRecordModal } from './components/StudentRecordModal';

export function App() {
  const [user, setUser] = useState<User | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);

  // Theme with persistence
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined' && window.localStorage) {
      const saved = localStorage.getItem('campusmind_theme');
      if (saved === 'dark') return true;
      if (saved === 'light') return false;
    }
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Navigation & Layout
  const [currentView, setCurrentView] = useState<'chat' | 'admin'>('chat');
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [desktopSidebarCollapsed, setDesktopSidebarCollapsed] = useState(false);

  // Conversations State
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  // Mention & Workflow State
  const [availableMentions, setAvailableMentions] = useState<MentionItem[]>([]);
  const [showPrincipalModal, setShowPrincipalModal] = useState(false);
  const [studentRecordModal, setStudentRecordModal] = useState<{
    isOpen: boolean;
    record: StudentRecord | null;
    error: string | null;
    loading: boolean;
  }>({
    isOpen: false,
    record: null,
    error: null,
    loading: false,
  });

  // Apply dark mode class to root HTML & persist
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.setItem('campusmind_theme', 'dark');
      }
    } else {
      document.documentElement.classList.remove('dark');
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.setItem('campusmind_theme', 'light');
      }
    }
  }, [darkMode]);

  // Initial authentication check
  useEffect(() => {
    const initAuth = async () => {
      const token = api.getToken();
      if (token) {
        try {
          const profile = await api.getMe();
          setUser(profile);
        } catch {
          api.setToken(null);
          setUser(null);
          setShowLoginModal(true);
        }
      } else {
        setShowLoginModal(true);
      }
      setAuthChecked(true);
    };

    initAuth();
  }, []);

  // Fetch conversations and mentions when user is authenticated
  useEffect(() => {
    if (user) {
      loadConversations();
      loadMentions();
    } else {
      setConversations([]);
      setMessages([]);
      setActiveConversationId(null);
    }
  }, [user]);

  const loadConversations = async () => {
    try {
      const list = await api.getConversations();
      setConversations(list);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  const loadMentions = async () => {
    try {
      const mentions = await api.getMentions();
      setAvailableMentions(mentions);
    } catch (err) {
      console.error('Failed to load mentions:', err);
    }
  };

  const handleSelectConversation = async (convId: string) => {
    setActiveConversationId(convId);
    setCurrentView('chat');
    try {
      const detail = await api.getConversation(convId);
      setMessages(detail.messages || []);
    } catch (err) {
      console.error('Failed to load conversation thread:', err);
    }
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
    setCurrentView('chat');
  };

  const handleRenameConversation = async (convId: string, newTitle: string) => {
    try {
      const updated = await api.renameConversation(convId, newTitle);
      setConversations((prev) =>
        prev.map((c) => (c.id === convId ? { ...c, title: updated.title } : c))
      );
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to rename conversation');
    }
  };

  const handleDeleteConversation = async (convId: string) => {
    try {
      await api.deleteConversation(convId);
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (activeConversationId === convId) {
        handleNewChat();
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete conversation');
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isGenerating) return;

    // Optimistically push user message
    const optimisticUserMsg: Message = {
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimisticUserMsg]);
    setIsGenerating(true);

    try {
      const res = await api.sendQuery(text, activeConversationId || undefined);

      const assistantMsg: Message = {
        id: res.message_id,
        role: 'assistant',
        content: res.answer,
        citations: res.citations,
        insufficient_evidence: res.insufficient_evidence,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);

      // Set active conversation ID if it was newly created
      if (!activeConversationId && res.conversation_id) {
        setActiveConversationId(res.conversation_id);
      }

      // Reload conversation list
      loadConversations();
    } catch (err: unknown) {
      const errorMsg: Message = {
        role: 'assistant',
        content: `Error: ${err instanceof Error ? err.message : 'Failed to process request. Please try again.'}`,
        error: true,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleTriggerMentionWorkflow = async (workflow: string, key: string) => {
    if (workflow === 'principal_elevation') {
      setShowPrincipalModal(true);
    } else if (workflow === 'student_records' || workflow === 'student_lookup') {
      const targetRoll = key.startsWith('@') ? key.slice(1) : key;
      const lookupIdentifier = targetRoll === 'student' ? (user?.username || '') : targetRoll;

      setStudentRecordModal({
        isOpen: true,
        record: null,
        error: null,
        loading: true,
      });

      try {
        const record = await api.getStudentRecord(lookupIdentifier);
        setStudentRecordModal({
          isOpen: true,
          record,
          error: null,
          loading: false,
        });
      } catch (err: unknown) {
        setStudentRecordModal({
          isOpen: true,
          record: null,
          error: err instanceof Error ? err.message : 'Failed to retrieve student record',
          loading: false,
        });
      }
    }
  };

  const handleLogout = () => {
    api.logout();
    setUser(null);
    setShowLoginModal(true);
  };

  const handleLoginSuccess = (authenticatedUser: User) => {
    setUser(authenticatedUser);
    setShowLoginModal(false);
  };

  const handlePrincipalElevationSuccess = (elevatedUser: User) => {
    setUser(elevatedUser);
    setShowPrincipalModal(false);
  };

  const activeConvTitle = conversations.find((c) => c.id === activeConversationId)?.title;

  if (!authChecked) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#F7F7F5] dark:bg-[#151515]">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-[#171717] border-t-transparent dark:border-[#F1F1F1]" />
      </div>
    );
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#F7F7F5] text-[#1C1C1C] dark:bg-[#151515] dark:text-[#F3F3F3] font-sans">
      {/* Sidebar Navigation */}
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        onRenameConversation={handleRenameConversation}
        onDeleteConversation={handleDeleteConversation}
        user={user}
        onLogout={handleLogout}
        currentView={currentView}
        onChangeView={setCurrentView}
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode(!darkMode)}
        isOpen={mobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
        isCollapsed={desktopSidebarCollapsed}
        onToggleCollapse={() => setDesktopSidebarCollapsed(true)}
      />

      {/* Main Content View (Chat vs Admin Knowledge Studio) */}
      <main className="flex flex-1 flex-col overflow-hidden">
        {currentView === 'admin' && user?.role === 'admin' ? (
          <AdminKnowledgeStudio onBackToChat={() => setCurrentView('chat')} />
        ) : (
          <ChatArea
            messages={messages}
            onSendMessage={handleSendMessage}
            isGenerating={isGenerating}
            user={user}
            onOpenMobileSidebar={() => setMobileSidebarOpen(true)}
            availableMentions={availableMentions}
            onTriggerMentionWorkflow={handleTriggerMentionWorkflow}
            conversationTitle={activeConvTitle}
            isDesktopSidebarCollapsed={desktopSidebarCollapsed}
            onToggleDesktopSidebar={() => setDesktopSidebarCollapsed(!desktopSidebarCollapsed)}
          />
        )}
      </main>

      {/* Modals */}
      <LoginModal
        isOpen={showLoginModal}
        onSuccess={handleLoginSuccess}
      />

      <PrincipalAuthModal
        isOpen={showPrincipalModal}
        onClose={() => setShowPrincipalModal(false)}
        onSuccess={handlePrincipalElevationSuccess}
      />

      <StudentRecordModal
        isOpen={studentRecordModal.isOpen}
        onClose={() =>
          setStudentRecordModal((prev) => ({ ...prev, isOpen: false }))
        }
        record={studentRecordModal.record}
        error={studentRecordModal.error}
        loading={studentRecordModal.loading}
      />
    </div>
  );
}

export default App;
