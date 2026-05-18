import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FolderOpen,
  Upload,
  FileText,
  Trash2,
  Eye,
  Plus,
  Search,
  Filter,
  X,
  RefreshCw,
  File,
  CheckCircle,
} from 'lucide-react';
import api from '../apiClient';
import toast from 'react-hot-toast';

const DOC_TYPE_META = {
  base_policy: { label: 'Base Policy',  color: '#818cf8', bg: 'rgba(99,102,241,0.12)',  border: 'rgba(99,102,241,0.25)'  },
  rider:       { label: 'Rider',        color: '#34d399', bg: 'rgba(16,185,129,0.12)',  border: 'rgba(16,185,129,0.25)'  },
  amendment:   { label: 'Amendment',    color: '#fbbf24', bg: 'rgba(245,158,11,0.12)',  border: 'rgba(245,158,11,0.25)'  },
  email:       { label: 'Email',        color: '#f472b6', bg: 'rgba(244,114,182,0.12)', border: 'rgba(244,114,182,0.25)' },
};

const DocumentManager = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [dragover, setDragover] = useState(false);
  const [filters, setFilters] = useState({ type: 'all', search: '' });
  const fileInputRef = useRef(null);

  const fetchDocuments = async () => {
    try {
      const response = await api.get('/api/documents');
      setDocuments(Array.isArray(response.data) ? response.data : []);
    } catch {
      toast.error('Failed to load documents');
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDocuments(); }, []);

  const uploadFiles = async (files) => {
    if (!files.length) return;
    setUploading(true);

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const ext = file.name.split('.').pop().toLowerCase();
      if (!['pdf', 'docx', 'txt', 'html', 'doc'].includes(ext)) {
        toast.error(`${file.name}: Unsupported format`);
        continue;
      }

      setUploadProgress({ name: file.name, index: i + 1, total: files.length });
      const formData = new FormData();
      formData.append('file', file);

      try {
        await api.post('/api/documents/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        toast.success(`✓ ${file.name} processed`, { duration: 2000 });
      } catch (err) {
        const msg = err.response?.data?.detail || `Failed to upload ${file.name}`;
        toast.error(msg);
      }
    }

    setUploading(false);
    setUploadProgress(null);
    fetchDocuments();
  };

  const handleFileInput = (e) => {
    if (e.target.files) uploadFiles(Array.from(e.target.files));
    e.target.value = '';
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragover(false);
    const files = Array.from(e.dataTransfer.files);
    uploadFiles(files);
  };

  const handleDeleteDocument = async (docId, docName) => {
    if (!window.confirm(`Delete "${docName}"?`)) return;
    try {
      await api.delete(`/api/documents/${docId}`);
      toast.success('Document removed');
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to delete document';
      toast.error(msg);
    }
  };

  const filteredDocs = documents.filter((doc) => {
    if (filters.search && !(doc.name || '').toLowerCase().includes(filters.search.toLowerCase())) return false;
    if (filters.type !== 'all' && doc.type !== filters.type) return false;
    return true;
  });

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <div className="spinner" />
        <p className="text-sm" style={{ color: '#64748b' }}>Loading documents…</p>
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <FolderOpen className="h-6 w-6" style={{ color: '#818cf8' }} />
            <h1 className="page-title">Document Manager</h1>
          </div>
          <p className="page-subtitle">Upload and manage policy documents for AI analysis</p>
        </div>
        <div className="flex gap-2">
          <button onClick={fetchDocuments} className="btn-secondary text-sm">
            <RefreshCw className="h-4 w-4" />
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn-primary text-sm"
          >
            <Plus className="h-4 w-4" /> Upload Doc
          </button>
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.doc,.docx,.txt,.html"
        onChange={handleFileInput}
        className="hidden"
        id="file-upload"
      />

      {/* Upload Zone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <div
          className={`upload-zone ${dragover ? 'dragover' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragover(true); }}
          onDragLeave={() => setDragover(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          {uploading && uploadProgress ? (
            <div className="space-y-3">
              <RefreshCw className="h-10 w-10 mx-auto animate-spin" style={{ color: '#6366f1' }} />
              <p className="text-sm font-medium" style={{ color: '#818cf8' }}>
                Uploading {uploadProgress.name}…
              </p>
              <p className="text-xs" style={{ color: '#64748b' }}>
                {uploadProgress.index} of {uploadProgress.total}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <Upload
                className="h-12 w-12 mx-auto transition-transform"
                style={{ color: dragover ? '#818cf8' : '#334155' }}
              />
              <div>
                <p className="text-base font-semibold" style={{ color: dragover ? '#818cf8' : '#64748b' }}>
                  {dragover ? 'Release to upload' : 'Drag & drop or click to upload'}
                </p>
                <p className="text-xs mt-1" style={{ color: '#334155' }}>
                  Supports PDF, DOCX, TXT, HTML • Multiple files allowed
                </p>
              </div>
            </div>
          )}
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card mb-6"
        style={{ padding: '0.875rem 1rem' }}
      >
        <div className="flex items-center gap-3">
          <Filter className="h-4 w-4 flex-shrink-0" style={{ color: '#818cf8' }} />
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4" style={{ color: '#475569' }} />
            <input
              type="text"
              placeholder="Search documents…"
              value={filters.search}
              onChange={(e) => setFilters((p) => ({ ...p, search: e.target.value }))}
              className="input-field pl-9 py-2"
            />
          </div>
          <select
            value={filters.type}
            onChange={(e) => setFilters((p) => ({ ...p, type: e.target.value }))}
            className="input-field py-2"
            style={{ appearance: 'none', minWidth: 140 }}
          >
            <option value="all">All Types</option>
            {Object.entries(DOC_TYPE_META).map(([k, m]) => (
              <option key={k} value={k}>{m.label}</option>
            ))}
          </select>
        </div>
      </motion.div>

      {/* Document Count */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm" style={{ color: '#64748b' }}>
          <span style={{ color: '#818cf8', fontWeight: 600 }}>{filteredDocs.length}</span> of{' '}
          <span style={{ color: '#94a3b8' }}>{documents.length}</span> documents
        </p>
      </div>

      {/* Documents Grid / List */}
      <div className="space-y-3">
        {filteredDocs.map((doc, index) => {
          const meta = DOC_TYPE_META[doc.type] || DOC_TYPE_META.base_policy;
          const uploadedAt = doc.uploaded_at
            ? new Date(doc.uploaded_at).toLocaleDateString('en-IN', {
                day: '2-digit', month: 'short', year: 'numeric',
              })
            : 'Unknown date';

          return (
            <motion.div
              key={doc.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.06 }}
              className="card"
              style={{ padding: '1rem 1.25rem' }}
            >
              <div className="flex items-center gap-4">
                {/* File icon */}
                <div
                  className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ background: meta.bg, border: `1px solid ${meta.border}` }}
                >
                  <FileText className="h-5 w-5" style={{ color: meta.color }} />
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold truncate mb-1" style={{ color: '#f1f5f9' }}>
                    {doc.name}
                  </p>
                  <div className="flex flex-wrap items-center gap-2 text-xs" style={{ color: '#64748b' }}>
                    <span
                      className="font-semibold px-2 py-0.5 rounded-full"
                      style={{ background: meta.bg, color: meta.color, border: `1px solid ${meta.border}` }}
                    >
                      {meta.label}
                    </span>
                    <span>{doc.chunk_count || 0} chunks</span>
                    <span>{uploadedAt}</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={() => setSelectedDocument(doc)}
                    className="btn-secondary text-xs py-1.5 px-3"
                  >
                    <Eye className="h-3.5 w-3.5" /> View
                  </button>
                  <button
                    onClick={() => handleDeleteDocument(doc.id, doc.name)}
                    className="btn-danger text-xs py-1.5 px-3"
                  >
                    <Trash2 className="h-3.5 w-3.5" /> Delete
                  </button>
                </div>
              </div>
            </motion.div>
          );
        })}

        {filteredDocs.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <FolderOpen className="h-14 w-14 mx-auto mb-4" style={{ color: '#1e293b' }} />
            <p className="text-base font-medium mb-1" style={{ color: '#334155' }}>
              No documents found
            </p>
            <p className="text-sm mb-6" style={{ color: '#475569' }}>
              Upload a PDF or DOCX policy document to get started
            </p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="btn-primary text-sm mx-auto"
            >
              <Upload className="h-4 w-4" /> Upload First Document
            </button>
          </motion.div>
        )}
      </div>

      {/* Document Detail Modal */}
      <AnimatePresence>
        {selectedDocument && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 flex items-center justify-center z-50 px-4"
            style={{ background: 'rgba(2,6,23,0.85)', backdropFilter: 'blur(8px)' }}
            onClick={(e) => { if (e.target === e.currentTarget) setSelectedDocument(null); }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.92, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.92, y: 20 }}
              className="card max-w-lg w-full"
              style={{ background: 'rgba(15,23,42,0.98)' }}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-base font-bold" style={{ color: '#f1f5f9' }}>Document Details</h2>
                <button onClick={() => setSelectedDocument(null)} style={{ color: '#64748b' }}>
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="space-y-4">
                {[
                  { label: 'File Name', value: selectedDocument.name },
                  { label: 'Document Type', value: DOC_TYPE_META[selectedDocument.type]?.label || selectedDocument.type },
                  { label: 'Text Chunks', value: `${selectedDocument.chunk_count || 0} chunks extracted` },
                  { label: 'Uploaded', value: selectedDocument.uploaded_at
                      ? new Date(selectedDocument.uploaded_at).toLocaleString()
                      : 'N/A' },
                  { label: 'File ID', value: selectedDocument.id },
                ].map(({ label, value }) => (
                  <div key={label} className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0" style={{ background: '#6366f1' }} />
                    <div>
                      <p className="text-xs font-semibold mb-0.5" style={{ color: '#475569' }}>{label}</p>
                      <p className="text-sm break-all" style={{ color: '#94a3b8' }}>{value}</p>
                    </div>
                  </div>
                ))}

                <div className="pt-4 border-t" style={{ borderColor: 'rgba(99,102,241,0.15)' }}>
                  <div className="flex items-center gap-2 text-xs" style={{ color: '#34d399' }}>
                    <CheckCircle className="h-3.5 w-3.5" />
                    Ready for semantic retrieval
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DocumentManager;
