import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  UploadCloud,
  FileText,
  Trash2,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Search,
  Layers,
  FileCheck,
  Clock,
  Info,
  X,
  ArrowLeft,
} from 'lucide-react';
import { api } from '../lib/api-client';
import type { DocumentRead, AdminStats, UserRole } from '../types';

interface AdminKnowledgeStudioProps {
  onBackToChat: () => void;
}

export const AdminKnowledgeStudio: React.FC<AdminKnowledgeStudioProps> = ({ onBackToChat }) => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [documents, setDocuments] = useState<DocumentRead[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Upload Form State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentTitle, setDocumentTitle] = useState('');
  const [audienceRole, setAudienceRole] = useState<UserRole>('student');
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Table Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [inspectingDoc, setInspectingDoc] = useState<DocumentRead | null>(null);

  const fetchData = async () => {
    try {
      setError(null);
      const [statsData, docsData] = await Promise.all([
        api.getAdminStats(),
        api.getAdminDocuments(),
      ]);
      setStats(statsData);
      setDocuments(docsData.documents);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch knowledge base data');
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      handleFileSelected(file);
    }
  };

  const handleFileSelected = (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!['pdf', 'docx', 'txt'].includes(ext || '')) {
      setUploadMessage({
        type: 'error',
        text: `Invalid file extension .${ext}. Only PDF, DOCX, and TXT files are supported.`,
      });
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setUploadMessage({
        type: 'error',
        text: 'File size exceeds maximum permitted 10 MB limit.',
      });
      return;
    }
    setSelectedFile(file);
    if (!documentTitle) {
      setDocumentTitle(file.name.replace(/\.[^/.]+$/, ''));
    }
    setUploadMessage(null);
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setUploadMessage(null);

    try {
      const res = await api.uploadDocument(selectedFile, audienceRole, documentTitle.trim());
      setUploadMessage({
        type: 'success',
        text: res.message || `Document '${res.document.title}' ingested with ${res.document.chunk_count} vector chunks.`,
      });
      setSelectedFile(null);
      setDocumentTitle('');
      fetchData();
    } catch (err: unknown) {
      setUploadMessage({
        type: 'error',
        text: err instanceof Error ? err.message : 'Ingestion failed',
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: number, title: string) => {
    if (confirm(`Are you sure you want to delete '${title}'? This will delete all associated embeddings.`)) {
      try {
        await api.deleteDocument(docId);
        setDocuments((prev) => prev.filter((d) => d.id !== docId));
        if (inspectingDoc?.id === docId) setInspectingDoc(null);
        fetchData();
      } catch (err: unknown) {
        alert(err instanceof Error ? err.message : 'Failed to delete document');
      }
    }
  };

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch =
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.filename.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = roleFilter === 'all' || doc.audience_role === roleFilter;
    const matchesStatus = statusFilter === 'all' || doc.processing_status === statusFilter;
    return matchesSearch && matchesRole && matchesStatus;
  });

  return (
    <div className="flex-1 overflow-y-auto bg-[#F7F7F5] p-6 dark:bg-[#151515]">
      <div className="mx-auto max-w-5xl space-y-6">
        {/* Top Header */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-[#E6E5E1] pb-4 dark:border-[#343434]">
          <div>
            <div className="flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-[#1C1C1C] dark:text-[#F3F3F3]" />
              <h1 className="text-base font-semibold text-[#1C1C1C] dark:text-[#F3F3F3]">
                Knowledge Studio
              </h1>
            </div>
            <p className="mt-0.5 text-xs text-[#686868] dark:text-[#B5B5B5]">
              Institutional knowledge repository, audience clearance boundaries, and vector indices
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center gap-1.5 rounded-lg border border-[#E6E5E1] bg-[#FFFFFF] px-2.5 py-1.5 text-xs text-[#1C1C1C] hover:bg-[#F0F0ED] dark:border-[#343434] dark:bg-[#1D1D1D] dark:text-[#F3F3F3] dark:hover:bg-[#252525]"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            <button
              onClick={onBackToChat}
              className="flex items-center gap-1.5 rounded-lg bg-[#171717] px-3 py-1.5 text-xs font-medium text-[#FFFFFF] hover:bg-[#2A2A2A] dark:bg-[#F1F1F1] dark:text-[#181818] dark:hover:bg-[#E5E5E5] transition-colors"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              <span>Back to Chat</span>
            </button>
          </div>
        </div>

        {error && (
          <div className="rounded-lg border border-[#FEE2E2] bg-[#FEF2F2] p-3 text-xs text-[#B91C1C] dark:border-[#7F1D1D] dark:bg-[#450A0A] dark:text-[#FCA5A5] flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-xl border border-[#E6E5E1] bg-[#FFFFFF] p-3.5 dark:border-[#343434] dark:bg-[#1D1D1D]">
            <div className="flex items-center justify-between text-[#686868] dark:text-[#B5B5B5]">
              <span className="text-[11px] font-medium">Total Documents</span>
              <FileText className="h-3.5 w-3.5 text-[#1C1C1C] dark:text-[#F3F3F3]" />
            </div>
            <div className="mt-1.5 text-xl font-semibold text-[#1C1C1C] dark:text-[#F3F3F3]">
              {stats?.total_documents ?? '...'}
            </div>
            <span className="text-[10px] text-[#898989] dark:text-[#929292]">Approved campus policies</span>
          </div>

          <div className="rounded-xl border border-[#E6E5E1] bg-[#FFFFFF] p-3.5 dark:border-[#343434] dark:bg-[#1D1D1D]">
            <div className="flex items-center justify-between text-[#686868] dark:text-[#B5B5B5]">
              <span className="text-[11px] font-medium">Indexed</span>
              <FileCheck className="h-3.5 w-3.5 text-[#1C1C1C] dark:text-[#F3F3F3]" />
            </div>
            <div className="mt-1.5 text-xl font-semibold text-[#1C1C1C] dark:text-[#F3F3F3]">
              {stats?.completed_documents ?? '...'}
            </div>
            <span className="text-[10px] text-[#898989] dark:text-[#929292]">Available for retrieval</span>
          </div>

          <div className="rounded-xl border border-[#E6E5E1] bg-[#FFFFFF] p-3.5 dark:border-[#343434] dark:bg-[#1D1D1D]">
            <div className="flex items-center justify-between text-[#686868] dark:text-[#B5B5B5]">
              <span className="text-[11px] font-medium">Vector Chunks</span>
              <Layers className="h-3.5 w-3.5 text-[#1C1C1C] dark:text-[#F3F3F3]" />
            </div>
            <div className="mt-1.5 text-xl font-semibold text-[#1C1C1C] dark:text-[#F3F3F3]">
              {stats?.total_chunks ?? '...'}
            </div>
            <span className="text-[10px] text-[#898989] dark:text-[#929292]">pgvector embeddings</span>
          </div>

          <div className="rounded-xl border border-[#E6E5E1] bg-[#FFFFFF] p-3.5 dark:border-[#343434] dark:bg-[#1D1D1D]">
            <div className="flex items-center justify-between text-[#686868] dark:text-[#B5B5B5]">
              <span className="text-[11px] font-medium">Failures</span>
              <AlertCircle className="h-3.5 w-3.5 text-[#686868] dark:text-[#B5B5B5]" />
            </div>
            <div className="mt-1.5 text-xl font-semibold text-[#1C1C1C] dark:text-[#F3F3F3]">
              {stats?.failed_documents ?? 0}
            </div>
            <span className="text-[10px] text-[#898989] dark:text-[#929292]">Ingestion errors</span>
          </div>
        </div>

        {/* Upload Form */}
        <div className="rounded-xl border border-[#E6E5E1] bg-[#FFFFFF] p-5 dark:border-[#343434] dark:bg-[#1D1D1D]">
          <h2 className="text-xs font-semibold text-[#1C1C1C] dark:text-[#F3F3F3] flex items-center gap-2">
            <UploadCloud className="h-4 w-4 text-[#1C1C1C] dark:text-[#F3F3F3]" />
            Ingest Document
          </h2>
          <p className="mt-0.5 text-xs text-[#686868] dark:text-[#B5B5B5]">
            Upload institutional guidelines (PDF, DOCX, TXT up to 10 MB). Documents are split into semantic chunks and embedded into the vector index.
          </p>

          {uploadMessage && (
            <div
              className={`mt-3 rounded-lg p-2.5 text-xs flex items-center gap-2 ${
                uploadMessage.type === 'success'
                  ? 'border border-[#BBF7D0] bg-[#F0FDF4] text-[#15803D] dark:border-[#14532D] dark:bg-[#052E16] dark:text-[#4ADE80]'
                  : 'border border-[#FEE2E2] bg-[#FEF2F2] text-[#B91C1C] dark:border-[#7F1D1D] dark:bg-[#450A0A] dark:text-[#FCA5A5]'
              }`}
            >
              {uploadMessage.type === 'success' ? (
                <CheckCircle className="h-4 w-4 shrink-0" />
              ) : (
                <AlertCircle className="h-4 w-4 shrink-0" />
              )}
              <span>{uploadMessage.text}</span>
            </div>
          )}

          <form onSubmit={handleUploadSubmit} className="mt-3.5 space-y-3">
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleFileDrop}
              onClick={() => document.getElementById('file-input')?.click()}
              className="flex flex-col items-center justify-center rounded-xl border border-dashed border-[#E6E5E1] bg-[#F7F7F5] p-5 text-center cursor-pointer hover:border-[#171717] transition-colors dark:border-[#343434] dark:bg-[#252525] dark:hover:border-[#F1F1F1]"
            >
              <input
                id="file-input"
                type="file"
                accept=".pdf,.docx,.txt"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileSelected(e.target.files[0]);
                  }
                }}
              />
              <UploadCloud className="h-5 w-5 text-[#898989] dark:text-[#929292] mb-1.5" />
              {selectedFile ? (
                <div>
                  <span className="text-xs font-medium text-[#1C1C1C] dark:text-[#F3F3F3]">
                    {selectedFile.name}
                  </span>
                  <p className="text-[10px] text-[#686868] dark:text-[#B5B5B5]">
                    {(selectedFile.size / 1024).toFixed(1)} KB — Ready to upload
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-xs font-medium text-[#1C1C1C] dark:text-[#F3F3F3]">
                    Click to select file or drag and drop
                  </p>
                  <p className="mt-0.5 text-[10px] text-[#898989] dark:text-[#929292]">
                    Supported formats: PDF, DOCX, TXT (Maximum 10 MB)
                  </p>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div>
                <label className="block text-xs font-medium text-[#1C1C1C] dark:text-[#F3F3F3] mb-1">
                  Document Title
                </label>
                <input
                  type="text"
                  value={documentTitle}
                  onChange={(e) => setDocumentTitle(e.target.value)}
                  placeholder="e.g. Academic Calendar 2026"
                  className="w-full rounded-lg border border-[#E6E5E1] bg-[#FFFFFF] px-3 py-1.5 text-xs text-[#1C1C1C] focus:border-[#7D91C9] focus:outline-none dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3] dark:focus:border-[#9EAFE8]"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[#1C1C1C] dark:text-[#F3F3F3] mb-1">
                  Audience Clearance
                </label>
                <select
                  value={audienceRole}
                  onChange={(e) => setAudienceRole(e.target.value as UserRole)}
                  className="w-full rounded-lg border border-[#E6E5E1] bg-[#FFFFFF] px-3 py-1.5 text-xs text-[#1C1C1C] focus:border-[#7D91C9] focus:outline-none dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3] dark:focus:border-[#9EAFE8]"
                >
                  <option value="student">Student (Public / Student body access)</option>
                  <option value="faculty">Faculty (Faculty and staff only)</option>
                  <option value="admin">Administrator (Confidential institutional only)</option>
                </select>
              </div>
            </div>

            <div className="flex items-center justify-between pt-1">
              <span className="text-[11px] text-[#898989] dark:text-[#929292] flex items-center gap-1">
                <Info className="h-3 w-3" /> Clearance is verified prior to semantic retrieval.
              </span>

              <button
                type="submit"
                disabled={!selectedFile || uploading}
                className="flex items-center gap-1.5 rounded-lg bg-[#171717] px-3.5 py-1.5 text-xs font-medium text-[#FFFFFF] hover:bg-[#2A2A2A] disabled:opacity-50 transition-colors dark:bg-[#F1F1F1] dark:text-[#181818] dark:hover:bg-[#E5E5E5] cursor-pointer"
              >
                {uploading ? (
                  <>
                    <div className="h-3 w-3 animate-spin rounded-full border-2 border-white border-t-transparent dark:border-[#181818]" />
                    <span>Processing Ingestion...</span>
                  </>
                ) : (
                  <>
                    <UploadCloud className="h-3.5 w-3.5" />
                    <span>Ingest Document</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Document Management Table */}
        <div className="rounded-xl border border-[#E6E5E1] bg-[#FFFFFF] shadow-xs dark:border-[#343434] dark:bg-[#1D1D1D] overflow-hidden">
          {/* Table Controls */}
          <div className="flex flex-col gap-2.5 border-b border-[#E6E5E1] p-3 sm:flex-row sm:items-center sm:justify-between dark:border-[#343434]">
            <div className="flex items-center gap-2">
              <h3 className="text-xs font-semibold text-[#1C1C1C] dark:text-[#F3F3F3]">
                Ingested Documents
              </h3>
              <span className="rounded border border-[#E6E5E1] bg-[#F7F7F5] px-1.5 py-0.2 text-[10px] text-[#686868] dark:border-[#343434] dark:bg-[#252525] dark:text-[#B5B5B5]">
                {filteredDocs.length}
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <div className="relative">
                <Search className="absolute left-2 top-2 h-3 w-3 text-[#898989] dark:text-[#929292]" />
                <input
                  type="text"
                  placeholder="Filter by title..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] py-1 pl-6 pr-2.5 text-xs text-[#1C1C1C] focus:bg-white focus:outline-none dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3]"
                />
              </div>

              <select
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
                className="rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] px-2 py-1 text-xs text-[#1C1C1C] dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3]"
              >
                <option value="all">All Roles</option>
                <option value="student">Student</option>
                <option value="faculty">Faculty</option>
                <option value="admin">Admin</option>
              </select>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="rounded-lg border border-[#E6E5E1] bg-[#F7F7F5] px-2 py-1 text-xs text-[#1C1C1C] dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3]"
              >
                <option value="all">All Statuses</option>
                <option value="completed">Completed</option>
                <option value="pending">Pending</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-[#E6E5E1] bg-[#F7F7F5] text-[10px] font-medium uppercase text-[#686868] dark:border-[#343434] dark:bg-[#252525] dark:text-[#B5B5B5]">
                <tr>
                  <th className="px-3.5 py-2">Document</th>
                  <th className="px-3.5 py-2">Format</th>
                  <th className="px-3.5 py-2">Clearance</th>
                  <th className="px-3.5 py-2">Chunks</th>
                  <th className="px-3.5 py-2">Status</th>
                  <th className="px-3.5 py-2 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E6E5E1] dark:divide-[#343434]">
                {filteredDocs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-3.5 py-6 text-center text-xs text-[#898989] dark:text-[#929292]">
                      No documents found
                    </td>
                  </tr>
                ) : (
                  filteredDocs.map((doc) => (
                    <tr key={doc.id} className="hover:bg-[#F7F7F5]/60 dark:hover:bg-[#252525]/50 transition-colors">
                      <td className="px-3.5 py-2.5">
                        <div className="font-medium text-[#1C1C1C] dark:text-[#F3F3F3]">
                          {doc.title}
                        </div>
                        <div className="text-[10px] text-[#686868] dark:text-[#B5B5B5]">{doc.filename}</div>
                      </td>
                      <td className="px-3.5 py-2.5 uppercase font-mono text-[10px] text-[#898989] dark:text-[#929292]">
                        {doc.document_type}
                      </td>
                      <td className="px-3.5 py-2.5">
                        <span className="inline-flex items-center rounded border border-[#E6E5E1] bg-[#F7F7F5] px-1.5 py-0.5 text-[10px] font-medium capitalize text-[#1C1C1C] dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3]">
                          {doc.audience_role}
                        </span>
                      </td>
                      <td className="px-3.5 py-2.5 text-[#1C1C1C] dark:text-[#F3F3F3]">
                        {doc.chunk_count}
                      </td>
                      <td className="px-3.5 py-2.5">
                        {doc.processing_status === 'completed' ? (
                          <span className="inline-flex items-center gap-1 text-[11px] text-[#1C1C1C] dark:text-[#F3F3F3]">
                            <CheckCircle className="h-3 w-3" /> Indexed
                          </span>
                        ) : doc.processing_status === 'failed' ? (
                          <span className="inline-flex items-center gap-1 text-[11px] text-red-600 dark:text-red-400">
                            <AlertCircle className="h-3 w-3" /> Failed
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] text-[#686868] dark:text-[#B5B5B5]">
                            <Clock className="h-3 w-3" /> Processing
                          </span>
                        )}
                      </td>
                      <td className="px-3.5 py-2.5 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <button
                            onClick={() => setInspectingDoc(doc)}
                            className="rounded p-1 text-[#686868] hover:text-[#1C1C1C] dark:hover:text-[#F3F3F3]"
                            title="Inspect metadata"
                          >
                            <Info className="h-3.5 w-3.5" />
                          </button>
                          <button
                            onClick={() => handleDelete(doc.id, doc.title)}
                            className="rounded p-1 text-[#686868] hover:text-red-600 dark:hover:text-red-400"
                            title="Delete document"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Metadata Inspection Dialog */}
        {inspectingDoc && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-xs">
            <div className="w-full max-w-md rounded-xl border border-[#E6E5E1] bg-[#FFFFFF] p-5 shadow-xl dark:border-[#343434] dark:bg-[#1D1D1D]">
              <div className="flex items-center justify-between border-b border-[#E6E5E1] pb-2.5 dark:border-[#343434]">
                <h3 className="text-xs font-semibold text-[#1C1C1C] dark:text-[#F3F3F3]">
                  Document Metadata
                </h3>
                <button
                  onClick={() => setInspectingDoc(null)}
                  className="rounded p-1 text-[#686868] hover:text-[#1C1C1C] dark:hover:text-[#F3F3F3]"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <div className="mt-3 space-y-2 text-xs">
                <div>
                  <span className="text-[#686868] dark:text-[#B5B5B5]">Title:</span>{' '}
                  <span className="font-medium text-[#1C1C1C] dark:text-[#F3F3F3]">
                    {inspectingDoc.title}
                  </span>
                </div>
                <div>
                  <span className="text-[#686868] dark:text-[#B5B5B5]">Filename:</span>{' '}
                  <span className="font-mono text-[11px] text-[#1C1C1C] dark:text-[#F3F3F3]">
                    {inspectingDoc.filename}
                  </span>
                </div>
                <div>
                  <span className="text-[#686868] dark:text-[#B5B5B5]">SHA-256 Hash:</span>{' '}
                  <span className="font-mono text-[10px] text-[#686868] dark:text-[#B5B5B5] break-all block mt-0.5">
                    {inspectingDoc.content_hash}
                  </span>
                </div>
                <div>
                  <span className="text-[#686868] dark:text-[#B5B5B5]">Audience Role:</span>{' '}
                  <span className="font-medium capitalize text-[#1C1C1C] dark:text-[#F3F3F3]">
                    {inspectingDoc.audience_role}
                  </span>
                </div>
                <div>
                  <span className="text-[#686868] dark:text-[#B5B5B5]">Vector Chunks:</span>{' '}
                  <span className="text-[#1C1C1C] dark:text-[#F3F3F3]">
                    {inspectingDoc.chunk_count}
                  </span>
                </div>
                <div>
                  <span className="text-[#686868] dark:text-[#B5B5B5]">File Size:</span>{' '}
                  <span className="text-[#1C1C1C] dark:text-[#F3F3F3]">
                    {(inspectingDoc.file_size_bytes / 1024).toFixed(1)} KB
                  </span>
                </div>
                <div>
                  <span className="text-[#686868] dark:text-[#B5B5B5]">Ingested:</span>{' '}
                  <span className="text-[#1C1C1C] dark:text-[#F3F3F3]">
                    {new Date(inspectingDoc.created_at).toLocaleString()}
                  </span>
                </div>
                {inspectingDoc.error_message && (
                  <div className="rounded-lg border border-[#FEE2E2] bg-[#FEF2F2] p-2 text-xs text-[#B91C1C] dark:border-[#7F1D1D] dark:bg-[#450A0A] dark:text-[#FCA5A5]">
                    {inspectingDoc.error_message}
                  </div>
                )}
              </div>
              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => setInspectingDoc(null)}
                  className="rounded-lg border border-[#E6E5E1] bg-[#FFFFFF] px-3 py-1.5 text-xs text-[#1C1C1C] hover:bg-[#F0F0ED] dark:border-[#343434] dark:bg-[#252525] dark:text-[#F3F3F3]"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
