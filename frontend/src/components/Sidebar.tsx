import React, { useState, useEffect } from 'react';
import {
  MessageSquare,
  Plus,
  Search,
  Trash2,
  Edit2,
  Check,
  X,
  BookOpen,
  LogOut,
  Moon,
  Sun,
  Shield,
  GraduationCap,
  PanelLeftClose,
} from 'lucide-react';
import type { ConversationSummary, User } from '../types';

interface SidebarProps {
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  onRenameConversation: (id: string, newTitle: string) => Promise<void>;
  onDeleteConversation: (id: string) => Promise<void>;
  user: User | null;
  onLogout: () => void;
  currentView: 'chat' | 'admin';
  onChangeView: (view: 'chat' | 'admin') => void;
  darkMode: boolean;
  onToggleDarkMode: () => void;
  isOpen: boolean;
  onCloseMobile: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onRenameConversation,
  onDeleteConversation,
  user,
  onLogout,
  currentView,
  onChangeView,
  darkMode,
  onToggleDarkMode,
  isOpen,
  onCloseMobile,
  isCollapsed,
  onToggleCollapse,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  // Close mobile drawer on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onCloseMobile();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onCloseMobile]);

  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const startRename = (conv: ConversationSummary, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditTitle(conv.title);
  };

  const handleRenameSubmit = async (convId: string, e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (editTitle.trim()) {
      await onRenameConversation(convId, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleDelete = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this conversation?')) {
      await onDeleteConversation(convId);
    }
  };

  // Date categorization
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const yesterday = today - 86400000;
  const lastWeek = today - 7 * 86400000;

  const grouped = {
    today: [] as ConversationSummary[],
    yesterday: [] as ConversationSummary[],
    lastWeek: [] as ConversationSummary[],
    older: [] as ConversationSummary[],
  };

  filteredConversations.forEach((c) => {
    const time = new Date(c.updated_at || c.created_at).getTime();
    if (time >= today) {
      grouped.today.push(c);
    } else if (time >= yesterday) {
      grouped.yesterday.push(c);
    } else if (time >= lastWeek) {
      grouped.lastWeek.push(c);
    } else {
      grouped.older.push(c);
    }
  });

  const renderConversationGroup = (title: string, items: ConversationSummary[]) => {
    if (items.length === 0) return null;
    return (
      <div className="mb-4">
        <div className="px-3 py-1 text-[11px] font-medium tracking-normal text-[#686868] dark:text-[#B5B5B5]">
          {title}
        </div>
        <div className="space-y-0.5">
          {items.map((conv) => {
            const isActive = activeConversationId === conv.id && currentView === 'chat';
            const isEditing = editingId === conv.id;

            return (
              <div
                key={conv.id}
                onClick={() => {
                  onSelectConversation(conv.id);
                  onCloseMobile();
                }}
                className={`group relative flex items-center justify-between rounded-lg px-3 py-2 text-xs transition-colors cursor-pointer ${
                  isActive
                    ? 'bg-[#F0F0ED] text-[#1C1C1C] font-semibold dark:bg-[#252525] dark:text-[#F3F3F3]'
                    : 'text-[#1C1C1C] hover:bg-[#F0F0ED]/70 dark:text-[#F3F3F3] dark:hover:bg-[#252525]/70'
                }`}
              >
                <div className="flex items-center gap-2 overflow-hidden pr-1 w-full">
                  <MessageSquare
                    className={`h-3.5 w-3.5 shrink-0 ${
                      isActive
                        ? 'text-[#1C1C1C] dark:text-[#F3F3F3]'
                        : 'text-[#898989] dark:text-[#929292]'
                    }`}
                  />
                  {isEditing ? (
                    <form
                      onSubmit={(e) => handleRenameSubmit(conv.id, e)}
                      onClick={(e) => e.stopPropagation()}
                      className="flex items-center gap-1 w-full"
                    >
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        autoFocus
                        className="w-full rounded border border-[#171717] bg-white px-1.5 py-0.5 text-xs text-[#1C1C1C] focus:outline-none dark:border-[#F1F1F1] dark:bg-[#1D1D1D] dark:text-[#F3F3F3]"
                      />
                      <button
                        type="submit"
                        className="p-0.5 text-[#1C1C1C] dark:text-[#F3F3F3]"
                        title="Save title"
                      >
                        <Check className="h-3.5 w-3.5" />
                      </button>
                      <button
                        type="button"
                        onClick={() => setEditingId(null)}
                        className="p-0.5 text-[#898989] hover:text-red-500"
                        title="Cancel"
                      >
                        <X className="h-3.5 w-3.5" />
                      </button>
                    </form>
                  ) : (
                    <span className="truncate">{conv.title}</span>
                  )}
                </div>

                {!isEditing && (
                  <div className="hidden items-center gap-0.5 group-hover:flex shrink-0">
                    <button
                      onClick={(e) => startRename(conv, e)}
                      className="p-1 text-[#898989] hover:text-[#1C1C1C] dark:hover:text-[#F3F3F3]"
                      title="Rename"
                    >
                      <Edit2 className="h-3 w-3" />
                    </button>
                    <button
                      onClick={(e) => handleDelete(conv.id, e)}
                      className="p-1 text-[#898989] hover:text-red-600 dark:hover:text-red-400"
                      title="Delete"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'admin':
        return (
          <span className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-medium bg-[#F0F0ED] text-[#1C1C1C] border border-[#E6E5E1] dark:bg-[#252525] dark:text-[#F3F3F3] dark:border-[#343434]">
            <Shield className="h-2.5 w-2.5" /> Admin
          </span>
        );
      case 'faculty':
        return (
          <span className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-medium bg-[#F0F0ED] text-[#1C1C1C] border border-[#E6E5E1] dark:bg-[#252525] dark:text-[#F3F3F3] dark:border-[#343434]">
            <GraduationCap className="h-2.5 w-2.5" /> Faculty
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-medium bg-[#F0F0ED] text-[#686868] border border-[#E6E5E1] dark:bg-[#252525] dark:text-[#B5B5B5] dark:border-[#343434]">
            Student
          </span>
        );
    }
  };

  const initials = user?.full_name
    ? user.full_name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : user?.username?.slice(0, 2).toUpperCase() || 'CM';

  // Desktop collapsed state
  if (isCollapsed) {
    return null;
  }

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-black/30 backdrop-blur-xs lg:hidden"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-[#E6E5E1] bg-[#FFFFFF] transition-all duration-200 ease-in-out dark:border-[#343434] dark:bg-[#1D1D1D] lg:static lg:translate-x-0 ${
          isOpen ? 'translate-x-0 shadow-xl' : '-translate-x-full lg:shadow-none'
        }`}
      >
        {/* Brand Header & Collapse Toggle */}
        <div className="flex h-14 items-center justify-between border-b border-[#E6E5E1] px-4 dark:border-[#343434]">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold tracking-tight text-[#1C1C1C] dark:text-[#F3F3F3]">
                CampusMind
              </span>
              <span className="rounded border border-[#E6E5E1] bg-[#F7F7F5] px-1 py-0.2 text-[9px] font-mono text-[#686868] dark:border-[#343434] dark:bg-[#252525] dark:text-[#B5B5B5]">
                v1.0
              </span>
            </div>
            <p className="text-[11px] text-[#686868] dark:text-[#B5B5B5]">Institutional Assistant</p>
          </div>

          <div className="flex items-center gap-1">
            {/* Desktop Collapse Toggle */}
            {onToggleCollapse && (
              <button
                onClick={onToggleCollapse}
                className="hidden lg:flex rounded p-1 text-[#686868] hover:bg-[#F0F0ED] hover:text-[#1C1C1C] dark:hover:bg-[#252525] dark:hover:text-[#F3F3F3]"
                title="Collapse sidebar"
                aria-label="Collapse sidebar"
              >
                <PanelLeftClose className="h-4 w-4" />
              </button>
            )}

            {/* Mobile Close Button */}
            <button
              onClick={onCloseMobile}
              className="lg:hidden rounded p-1 text-[#686868] hover:bg-[#F0F0ED] hover:text-[#1C1C1C] dark:hover:bg-[#252525]"
              aria-label="Close sidebar"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Action Controls */}
        <div className="p-3 space-y-2">
          <button
            onClick={() => {
              onNewChat();
              onChangeView('chat');
              onCloseMobile();
            }}
            className="flex w-full items-center justify-center gap-1.5 rounded-lg border border-[#171717] bg-[#171717] px-3 py-2 text-xs font-medium text-[#FFFFFF] transition-colors hover:bg-[#2A2A2A] dark:border-[#F1F1F1] dark:bg-[#F1F1F1] dark:text-[#181818] dark:hover:bg-[#E5E5E5] focus:outline-none"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>New conversation</span>
          </button>

          {/* Search conversation */}
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-[#898989] dark:text-[#929292]" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] py-1.5 pl-8 pr-2.5 text-xs text-[#1C1C1C] placeholder-[#898989] transition-colors focus:border-[#7D91C9] focus:bg-white focus:outline-none dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3] dark:placeholder-[#929292] dark:focus:border-[#9EAFE8]"
            />
          </div>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto px-2 py-1">
          {filteredConversations.length === 0 ? (
            <div className="py-8 text-center">
              <p className="text-xs text-[#898989] dark:text-[#929292]">
                {searchQuery ? 'No matching conversations' : 'No past conversations'}
              </p>
            </div>
          ) : (
            <>
              {renderConversationGroup('Today', grouped.today)}
              {renderConversationGroup('Yesterday', grouped.yesterday)}
              {renderConversationGroup('Previous 7 Days', grouped.lastWeek)}
              {renderConversationGroup('Older', grouped.older)}
            </>
          )}
        </div>

        {/* Admin Navigation */}
        {user?.role === 'admin' && (
          <div className="border-t border-[#E6E5E1] p-2.5 dark:border-[#343434]">
            <button
              onClick={() => {
                onChangeView(currentView === 'admin' ? 'chat' : 'admin');
                onCloseMobile();
              }}
              className={`flex w-full items-center justify-between rounded-lg px-2.5 py-1.5 text-xs transition-colors ${
                currentView === 'admin'
                  ? 'bg-[#F0F0ED] text-[#1C1C1C] font-semibold dark:bg-[#252525] dark:text-[#F3F3F3]'
                  : 'text-[#1C1C1C] hover:bg-[#F0F0ED]/70 dark:text-[#F3F3F3] dark:hover:bg-[#252525]/70'
              }`}
            >
              <div className="flex items-center gap-2">
                <BookOpen className="h-3.5 w-3.5 text-[#1C1C1C] dark:text-[#F3F3F3]" />
                <span>Knowledge Studio</span>
              </div>
              <span className="text-[10px] uppercase font-mono tracking-wider opacity-70">Admin</span>
            </button>
          </div>
        )}

        {/* User Profile & Footer Controls */}
        <div className="border-t border-[#E6E5E1] p-3 dark:border-[#343434] bg-[#FFFFFF] dark:bg-[#1D1D1D]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#E6E5E1] bg-[#F7F7F5] text-xs font-semibold text-[#1C1C1C] dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3]">
                {initials}
              </div>
              <div className="truncate">
                <div className="truncate text-xs font-medium text-[#1C1C1C] dark:text-[#F3F3F3]">
                  {user?.full_name || user?.username || 'Guest'}
                </div>
                <div className="flex items-center gap-1.5 mt-0.5">
                  {user && getRoleBadge(user.role)}
                  <span className="truncate text-[10px] text-[#898989] dark:text-[#929292]">
                    @{user?.username}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-0.5 shrink-0">
              <button
                onClick={onToggleDarkMode}
                className="rounded p-1 text-[#686868] hover:bg-[#F0F0ED] hover:text-[#1C1C1C] dark:hover:bg-[#252525] dark:hover:text-[#F3F3F3]"
                title={darkMode ? 'Switch to Light theme' : 'Switch to Dark theme'}
                aria-label="Toggle theme"
              >
                {darkMode ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
              </button>
              <button
                onClick={onLogout}
                className="rounded p-1 text-[#686868] hover:bg-[#FEE2E2] hover:text-[#B91C1C] dark:hover:bg-[#450A0A] dark:hover:text-[#EF4444]"
                title="Sign out"
                aria-label="Sign out"
              >
                <LogOut className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
