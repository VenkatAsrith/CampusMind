import React, { useState } from 'react';
import { X, Shield, Lock, AlertCircle, ArrowRight } from 'lucide-react';
import { api } from '../lib/api-client';
import type { User } from '../types';

interface PrincipalAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (user: User) => void;
}

export const PrincipalAuthModal: React.FC<PrincipalAuthModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [username, setUsername] = useState('principal');
  const [password, setPassword] = useState('Principal123!');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await api.login(username.trim(), password);
      if (res.user.role !== 'admin') {
        throw new Error(
          `Elevation Denied: Account '${res.user.username}' holds role '${res.user.role}'. Only authorized Principal / Executive Administrator identities may access restricted institutional governance.`
        );
      }
      onSuccess(res.user);
      onClose();
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Authentication failed';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-xs">
      <div className="w-full max-w-sm rounded-xl border border-[#E6E5E1] bg-[#FFFFFF] shadow-xl dark:border-[#343434] dark:bg-[#1D1D1D] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#E6E5E1] px-5 py-3.5 dark:border-[#343434] bg-[#FFFFFF] dark:bg-[#1D1D1D]">
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-[#1C1C1C] dark:text-[#F3F3F3]" />
            <div>
              <h3 className="text-xs font-semibold text-[#1C1C1C] dark:text-[#F3F3F3]">
                Executive Authorization
              </h3>
              <p className="text-[10px] text-[#686868] dark:text-[#B5B5B5]">
                @principal Elevation Protocol
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded p-1 text-[#686868] hover:bg-[#F0F0ED] hover:text-[#1C1C1C] dark:hover:bg-[#252525] dark:hover:text-[#F3F3F3]"
            aria-label="Close modal"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Notice & Form */}
        <div className="p-5">
          <div className="mb-3.5 rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] p-2.5 text-xs text-[#686868] dark:border-[#343434] dark:bg-[#252525] dark:text-[#B5B5B5] leading-relaxed">
            <p className="font-medium text-[#1C1C1C] dark:text-[#F3F3F3] mb-1 flex items-center gap-1.5">
              <Lock className="h-3 w-3 text-[#1C1C1C] dark:text-[#F3F3F3]" /> Identity Verification Required
            </p>
            Typing @principal is an interaction shortcut, not a security credential. Authenticate with an executive administrator account to access restricted governance.
          </div>

          {error && (
            <div className="mb-3.5 flex items-start gap-2 rounded-lg border border-[#FEE2E2] bg-[#FEF2F2] p-2.5 text-xs text-[#B91C1C] dark:border-[#7F1D1D] dark:bg-[#450A0A] dark:text-[#FCA5A5]">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-[#1C1C1C] dark:text-[#F3F3F3] mb-1">
                Executive Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="principal"
                className="w-full rounded-lg border border-[#E6E5E1] bg-[#FFFFFF] px-3 py-1.5 text-xs text-[#1C1C1C] focus:border-[#7D91C9] focus:outline-none dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3] dark:focus:border-[#9EAFE8]"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-[#1C1C1C] dark:text-[#F3F3F3] mb-1">
                Executive Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••••••"
                className="w-full rounded-lg border border-[#E6E5E1] bg-[#FFFFFF] px-3 py-1.5 text-xs text-[#1C1C1C] focus:border-[#7D91C9] focus:outline-none dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3] dark:focus:border-[#9EAFE8]"
              />
            </div>

            <div className="pt-1">
              <button
                type="submit"
                disabled={loading}
                className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-[#171717] py-2 text-xs font-medium text-[#FFFFFF] hover:bg-[#2A2A2A] disabled:opacity-50 transition-colors dark:bg-[#F1F1F1] dark:text-[#181818] cursor-pointer"
              >
                {loading ? (
                  <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent dark:border-[#181818]" />
                ) : (
                  <>
                    <span>Confirm Elevation</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Quick Demo Pre-fill */}
          <div className="mt-4 pt-3 border-t border-[#E6E5E1] dark:border-[#343434]">
            <span className="text-[10px] text-[#898989] dark:text-[#929292] block mb-1.5">
              Available Test Executive Accounts:
            </span>
            <div className="flex gap-1.5">
              <button
                type="button"
                onClick={() => {
                  setUsername('principal');
                  setPassword('Principal123!');
                }}
                className="rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] px-2 py-1 text-[11px] text-[#1C1C1C] hover:bg-[#F0F0ED] dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3]"
              >
                principal
              </button>
              <button
                type="button"
                onClick={() => {
                  setUsername('admin1');
                  setPassword('AdminPassword123!');
                }}
                className="rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] px-2 py-1 text-[11px] text-[#1C1C1C] hover:bg-[#F0F0ED] dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3]"
              >
                admin1
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
