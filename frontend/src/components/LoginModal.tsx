import React, { useState } from 'react';
import { Lock, LogIn, AlertCircle, Shield, GraduationCap, User as UserIcon } from 'lucide-react';
import { api } from '../lib/api-client';
import type { User } from '../types';

interface LoginModalProps {
  isOpen: boolean;
  onSuccess: (user: User) => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onSuccess }) => {
  const [username, setUsername] = useState('23SS1A0535');
  const [password, setPassword] = useState('Password123!');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await api.login(username.trim(), password);
      onSuccess(res.user);
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Login failed';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const setDemoAccount = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-xs">
      <div className="w-full max-w-sm rounded-xl border border-[#E6E5E1] bg-[#FFFFFF] p-6 shadow-xl dark:border-[#343434] dark:bg-[#1D1D1D]">
        <div className="mb-5 text-center">
          <h2 className="text-lg font-semibold tracking-tight text-[#1C1C1C] dark:text-[#F3F3F3]">
            Sign in to CampusMind
          </h2>
          <p className="mt-1 text-xs text-[#686868] dark:text-[#B5B5B5]">
            Institutional assistant with role-verified campus knowledge
          </p>
        </div>

        {error && (
          <div className="mb-4 flex items-start gap-2 rounded-lg border border-[#FEE2E2] bg-[#FEF2F2] p-2.5 text-xs text-[#B91C1C] dark:border-[#7F1D1D] dark:bg-[#450A0A] dark:text-[#FCA5A5]">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          <div>
            <label className="block text-xs font-medium text-[#1C1C1C] dark:text-[#F3F3F3] mb-1">
              Roll number or username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              placeholder="e.g. 23SS1A0535 or student1"
              className="w-full rounded-lg border border-[#E6E5E1] bg-[#FFFFFF] px-3 py-2 text-xs text-[#1C1C1C] placeholder-[#898989] focus:border-[#7D91C9] focus:outline-none dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3] dark:placeholder-[#929292] dark:focus:border-[#9EAFE8]"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-[#1C1C1C] dark:text-[#F3F3F3] mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••••••"
              className="w-full rounded-lg border border-[#E6E5E1] bg-[#FFFFFF] px-3 py-2 text-xs text-[#1C1C1C] placeholder-[#898989] focus:border-[#7D91C9] focus:outline-none dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3] dark:placeholder-[#929292] dark:focus:border-[#9EAFE8]"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-[#171717] py-2 text-xs font-medium text-[#FFFFFF] transition-colors hover:bg-[#2A2A2A] disabled:opacity-50 dark:bg-[#F1F1F1] dark:text-[#181818] dark:hover:bg-[#E5E5E5] cursor-pointer"
          >
            {loading ? (
              <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent dark:border-[#181818]" />
            ) : (
              <>
                <LogIn className="h-3.5 w-3.5" />
                <span>Sign In</span>
              </>
            )}
          </button>
        </form>

        {/* Demo Accounts Quick-Select */}
        <div className="mt-5 pt-4 border-t border-[#E6E5E1] dark:border-[#343434]">
          <span className="text-[10px] font-medium text-[#898989] dark:text-[#929292] block mb-2 text-center uppercase tracking-wider">
            Quick-Select Test Accounts
          </span>
          <div className="grid grid-cols-2 gap-1.5 text-xs">
            <button
              type="button"
              onClick={() => setDemoAccount('23SS1A0535', 'Password123!')}
              className="flex items-center gap-1.5 rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] p-1.5 text-left hover:bg-[#F0F0ED] hover:border-[#171717] dark:border-[#343434] dark:bg-[#252525] dark:hover:bg-[#202020] dark:hover:border-[#F1F1F1]"
            >
              <UserIcon className="h-3 w-3 text-[#1C1C1C] dark:text-[#F3F3F3]" />
              <div className="truncate">
                <p className="font-medium text-[#1C1C1C] dark:text-[#F3F3F3] text-[11px] truncate">Student</p>
                <p className="text-[9px] text-[#686868] dark:text-[#B5B5B5] truncate">23SS1A0535</p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => setDemoAccount('faculty1', 'Password123!')}
              className="flex items-center gap-1.5 rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] p-1.5 text-left hover:bg-[#F0F0ED] hover:border-[#171717] dark:border-[#343434] dark:bg-[#252525] dark:hover:bg-[#202020] dark:hover:border-[#F1F1F1]"
            >
              <GraduationCap className="h-3 w-3 text-[#1C1C1C] dark:text-[#F3F3F3]" />
              <div className="truncate">
                <p className="font-medium text-[#1C1C1C] dark:text-[#F3F3F3] text-[11px] truncate">Faculty</p>
                <p className="text-[9px] text-[#686868] dark:text-[#B5B5B5] truncate">Dr. Taylor</p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => setDemoAccount('admin1', 'AdminPassword123!')}
              className="flex items-center gap-1.5 rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] p-1.5 text-left hover:bg-[#F0F0ED] hover:border-[#171717] dark:border-[#343434] dark:bg-[#252525] dark:hover:bg-[#202020] dark:hover:border-[#F1F1F1]"
            >
              <Shield className="h-3 w-3 text-[#1C1C1C] dark:text-[#F3F3F3]" />
              <div className="truncate">
                <p className="font-medium text-[#1C1C1C] dark:text-[#F3F3F3] text-[11px] truncate">Admin</p>
                <p className="text-[9px] text-[#686868] dark:text-[#B5B5B5] truncate">Knowledge Studio</p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => setDemoAccount('principal', 'Principal123!')}
              className="flex items-center gap-1.5 rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] p-1.5 text-left hover:bg-[#F0F0ED] hover:border-[#171717] dark:border-[#343434] dark:bg-[#252525] dark:hover:bg-[#202020] dark:hover:border-[#F1F1F1]"
            >
              <Lock className="h-3 w-3 text-[#1C1C1C] dark:text-[#F3F3F3]" />
              <div className="truncate">
                <p className="font-medium text-[#1C1C1C] dark:text-[#F3F3F3] text-[11px] truncate">Principal</p>
                <p className="text-[9px] text-[#686868] dark:text-[#B5B5B5] truncate">Executive</p>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
