import React, { useEffect, useRef } from 'react';
import type { MentionItem } from '../types';
import { UserCheck, Shield, HelpCircle, Sparkles } from 'lucide-react';

interface MentionMenuProps {
  mentions: MentionItem[];
  selectedIndex: number;
  onSelect: (mention: MentionItem) => void;
  position: { top: number; left: number };
}

export const MentionMenu: React.FC<MentionMenuProps> = ({
  mentions,
  selectedIndex,
  onSelect,
}) => {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (menuRef.current) {
      const activeElement = menuRef.current.children[selectedIndex + 1] as HTMLElement;
      if (activeElement) {
        activeElement.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [selectedIndex]);

  if (mentions.length === 0) return null;

  const getIcon = (workflow: string) => {
    switch (workflow) {
      case 'principal_elevation':
        return <Shield className="h-3.5 w-3.5 text-[#1C1C1C] dark:text-[#F3F3F3]" />;
      case 'student_records':
      case 'student_lookup':
        return <UserCheck className="h-3.5 w-3.5 text-[#1C1C1C] dark:text-[#F3F3F3]" />;
      case 'general_help':
        return <HelpCircle className="h-3.5 w-3.5 text-[#686868] dark:text-[#B5B5B5]" />;
      default:
        return <Sparkles className="h-3.5 w-3.5 text-[#1C1C1C] dark:text-[#F3F3F3]" />;
    }
  };

  return (
    <div
      ref={menuRef}
      className="absolute bottom-full left-0 mb-2 w-80 max-h-56 overflow-y-auto rounded-xl border border-[#E6E5E1] bg-[#FFFFFF] p-1.5 shadow-xl dark:border-[#343434] dark:bg-[#1D1D1D] z-50"
    >
      <div className="px-2.5 py-1 text-[10px] font-medium tracking-normal text-[#898989] dark:text-[#929292]">
        Verified commands & roles
      </div>
      {mentions.map((item, idx) => {
        const isSelected = idx === selectedIndex;
        return (
          <div
            key={item.key}
            onClick={() => onSelect(item)}
            className={`flex items-start gap-2.5 rounded-lg px-2.5 py-2 cursor-pointer transition-colors ${
              isSelected
                ? 'bg-[#F0F0ED] text-[#1C1C1C] dark:bg-[#252525] dark:text-[#F3F3F3]'
                : 'text-[#1C1C1C] hover:bg-[#F7F7F5] dark:text-[#F3F3F3] dark:hover:bg-[#252525]/50'
            }`}
          >
            <div className="mt-0.5 shrink-0">{getIcon(item.workflow)}</div>
            <div className="overflow-hidden">
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-semibold text-[#1C1C1C] dark:text-[#F3F3F3]">
                  {item.label}
                </span>
                <span className="rounded border border-[#E6E5E1] bg-[#F7F7F5] px-1 py-0.2 text-[9px] font-mono text-[#686868] dark:border-[#343434] dark:bg-[#252525] dark:text-[#B5B5B5]">
                  {item.required_role}
                </span>
              </div>
              <p className="truncate text-[11px] text-[#686868] dark:text-[#B5B5B5] mt-0.5">
                {item.description}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
};
