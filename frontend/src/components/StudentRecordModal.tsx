import React from 'react';
import { X, GraduationCap, CheckCircle2, AlertTriangle, ShieldCheck, BookOpen, Clock } from 'lucide-react';
import type { StudentRecord } from '../types';

interface StudentRecordModalProps {
  isOpen: boolean;
  onClose: () => void;
  record: StudentRecord | null;
  error?: string | null;
  loading?: boolean;
}

export const StudentRecordModal: React.FC<StudentRecordModalProps> = ({
  isOpen,
  onClose,
  record,
  error,
  loading,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-xs">
      <div className="w-full max-w-md rounded-xl border border-[#E6E5E1] bg-[#FFFFFF] shadow-xl dark:border-[#343434] dark:bg-[#1D1D1D] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#E6E5E1] px-5 py-3.5 dark:border-[#343434] bg-[#FFFFFF] dark:bg-[#1D1D1D]">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-4 w-4 text-[#1C1C1C] dark:text-[#F3F3F3]" />
            <div>
              <h3 className="text-xs font-semibold text-[#1C1C1C] dark:text-[#F3F3F3]">
                Verified Student Record
              </h3>
              <p className="text-[10px] text-[#686868] dark:text-[#B5B5B5]">
                Institutional Enrollment Database
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

        {/* Content Body */}
        <div className="p-5">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-8">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-[#171717] border-t-transparent dark:border-[#F1F1F1]" />
              <p className="mt-2 text-xs text-[#686868] dark:text-[#B5B5B5]">Retrieving student record...</p>
            </div>
          ) : error ? (
            <div className="rounded-lg border border-[#FEE2E2] bg-[#FEF2F2] p-3 text-xs text-[#B91C1C] dark:border-[#7F1D1D] dark:bg-[#450A0A] dark:text-[#FCA5A5]">
              <div className="flex items-start gap-2">
                <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold">Access Denied</h4>
                  <p className="mt-0.5 text-[11px] leading-relaxed">{error}</p>
                  <p className="mt-1.5 text-[10px] opacity-80">
                    Per institutional policy, users may only query records matching their authenticated identity.
                  </p>
                </div>
              </div>
            </div>
          ) : record ? (
            <div className="space-y-3.5">
              {/* Identity Details */}
              <div className="rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] p-3.5 dark:border-[#343434] dark:bg-[#252525]">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-[10px] font-medium text-[#686868] dark:text-[#B5B5B5] uppercase">
                      Roll Number
                    </span>
                    <div className="text-sm font-mono font-semibold text-[#1C1C1C] dark:text-[#F3F3F3]">
                      {record.roll_number}
                    </div>
                  </div>
                  <span className="inline-flex items-center gap-1 rounded border border-[#E6E5E1] bg-[#FFFFFF] px-2 py-0.5 text-[10px] font-medium text-[#1C1C1C] dark:border-[#343434] dark:bg-[#1D1D1D] dark:text-[#F3F3F3]">
                    <ShieldCheck className="h-3 w-3" /> Enrolled
                  </span>
                </div>
                <div className="mt-2.5 grid grid-cols-2 gap-2 pt-2.5 border-t border-[#E6E5E1] dark:border-[#343434] text-xs">
                  <div>
                    <span className="text-[10px] text-[#686868] dark:text-[#B5B5B5]">Full Name</span>
                    <p className="font-medium text-[#1C1C1C] dark:text-[#F3F3F3]">{record.full_name}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-[#686868] dark:text-[#B5B5B5]">Standing</span>
                    <p className="font-medium text-[#1C1C1C] dark:text-[#F3F3F3]">{record.academic_standing}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-[#686868] dark:text-[#B5B5B5]">Program</span>
                    <p className="text-[#1C1C1C] dark:text-[#F3F3F3]">{record.program}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-[#686868] dark:text-[#B5B5B5]">Semester</span>
                    <p className="text-[#1C1C1C] dark:text-[#F3F3F3]">{record.semester}</p>
                  </div>
                </div>
              </div>

              {/* Attendance Progress */}
              <div className="rounded-lg border border-[#E6E5E1] p-3 dark:border-[#343434]">
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5 text-[#686868] dark:text-[#B5B5B5]">
                    <Clock className="h-3 w-3" /> Current Attendance
                  </span>
                  <span className="font-semibold text-[#1C1C1C] dark:text-[#F3F3F3]">
                    {record.attendance_percentage}%
                  </span>
                </div>
                <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-[#E6E5E1] dark:bg-[#343434]">
                  <div
                    className="h-full rounded-full bg-[#171717] dark:bg-[#F1F1F1]"
                    style={{ width: `${Math.min(record.attendance_percentage, 100)}%` }}
                  />
                </div>
                <p className="mt-1 text-[10px] text-[#898989] dark:text-[#929292]">
                  Minimum 75% required for examination eligibility.
                </p>
              </div>

              {/* Registered Courses */}
              <div>
                <span className="text-xs font-medium text-[#1C1C1C] dark:text-[#F3F3F3] flex items-center gap-1.5 mb-1.5">
                  <BookOpen className="h-3.5 w-3.5 text-[#686868] dark:text-[#B5B5B5]" /> Registered Courses
                </span>
                <div className="space-y-1">
                  {record.registered_courses.map((course, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] px-2.5 py-1.5 text-xs text-[#1C1C1C] dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3]"
                    >
                      <span>{course}</span>
                      <CheckCircle2 className="h-3 w-3 text-[#1C1C1C] dark:text-[#F3F3F3]" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="flex justify-end border-t border-[#E6E5E1] px-5 py-2.5 dark:border-[#343434] bg-[#F7F7F5] dark:bg-[#1D1D1D]">
          <button
            onClick={onClose}
            className="rounded-lg border border-[#E6E5E1] bg-[#FFFFFF] px-3.5 py-1.5 text-xs font-medium text-[#1C1C1C] hover:bg-[#F0F0ED] dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3] dark:hover:bg-[#202020]"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
