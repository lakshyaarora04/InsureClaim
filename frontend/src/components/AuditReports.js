import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText,
  Download,
  Calendar,
  Filter,
  Eye,
  CheckCircle,
  XCircle,
  RefreshCw,
  X,
  Printer,
  Search,
} from 'lucide-react';
import api from '../apiClient';
import toast from 'react-hot-toast';

const AuditReports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState(null);
  const [filters, setFilters] = useState({
    dateFrom: '',
    dateTo: '',
    decision: 'all',
    search: '',
  });

  const fetchReports = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/audit/reports');
      setReports(Array.isArray(response.data) ? response.data : []);
    } catch {
      toast.error('Failed to load audit reports');
      setReports([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchReports(); }, []);

  const handleExportReport = async (reportId) => {
    try {
      const response = await api.get(`/api/audit/export/${reportId}`);
      const blob = new Blob([JSON.stringify(response.data, null, 2)], {
        type: 'application/json',
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `audit_report_${reportId}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Report exported!');
    } catch {
      toast.error('Failed to export report');
    }
  };

  const filteredReports = reports.filter((report) => {
    const q = (report.query || '').toLowerCase();
    if (filters.search && !q.includes(filters.search.toLowerCase())) return false;
    if (filters.decision !== 'all' && report.decision !== filters.decision) return false;
    if (filters.dateFrom && new Date(report.timestamp) < new Date(filters.dateFrom)) return false;
    if (filters.dateTo   && new Date(report.timestamp) > new Date(filters.dateTo))   return false;
    return true;
  });

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <div className="spinner" />
        <p className="text-sm" style={{ color: '#64748b' }}>Loading audit reports…</p>
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <FileText className="h-6 w-6" style={{ color: '#818cf8' }} />
            <h1 className="page-title">Audit Reports</h1>
          </div>
          <p className="page-subtitle">Complete decision trail for compliance and review</p>
        </div>
        <button onClick={fetchReports} className="btn-secondary text-sm">
          <RefreshCw className="h-4 w-4" /> Refresh
        </button>
      </div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card mb-6"
      >
        <div className="flex items-center gap-2 mb-4">
          <Filter className="h-4 w-4" style={{ color: '#818cf8' }} />
          <h3 className="text-sm font-semibold" style={{ color: '#f1f5f9' }}>Filters</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4" style={{ color: '#475569' }} />
            <input
              type="text"
              placeholder="Search query…"
              value={filters.search}
              onChange={(e) => setFilters((p) => ({ ...p, search: e.target.value }))}
              className="input-field pl-9"
            />
          </div>
          <select
            value={filters.decision}
            onChange={(e) => setFilters((p) => ({ ...p, decision: e.target.value }))}
            className="input-field"
            style={{ appearance: 'none' }}
          >
            <option value="all">All Decisions</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          <input
            type="date"
            value={filters.dateFrom}
            onChange={(e) => setFilters((p) => ({ ...p, dateFrom: e.target.value }))}
            className="input-field"
          />
          <input
            type="date"
            value={filters.dateTo}
            onChange={(e) => setFilters((p) => ({ ...p, dateTo: e.target.value }))}
            className="input-field"
          />
        </div>
      </motion.div>

      {/* Summary bar */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm" style={{ color: '#64748b' }}>
          Showing <span style={{ color: '#818cf8', fontWeight: 600 }}>{filteredReports.length}</span> of{' '}
          <span style={{ color: '#94a3b8' }}>{reports.length}</span> reports
        </p>
        {reports.length > 0 && (
          <div className="flex gap-3 text-xs">
            <span style={{ color: '#34d399' }}>
              {reports.filter((r) => r.decision === 'approved').length} approved
            </span>
            <span style={{ color: '#f87171' }}>
              {reports.filter((r) => r.decision === 'rejected').length} rejected
            </span>
          </div>
        )}
      </div>

      {/* Report list */}
      <div className="space-y-3">
        {filteredReports.map((report, index) => {
          const isApproved = report.decision === 'approved';
          const queryPreview = (report.query || 'Unnamed query').substring(0, 80);
          const confidence = report.confidence_score
            ? `${(report.confidence_score * 100).toFixed(1)}%`
            : 'N/A';

          return (
            <motion.div
              key={report.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="card"
              style={{ padding: '1rem 1.25rem' }}
            >
              <div className="flex items-center justify-between gap-4">
                {/* Left: status icon + info */}
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <div
                    className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{
                      background: isApproved ? 'rgba(16,185,129,0.12)' : 'rgba(239,68,68,0.12)',
                      border: `1px solid ${isApproved ? 'rgba(16,185,129,0.25)' : 'rgba(239,68,68,0.25)'}`,
                    }}
                  >
                    {isApproved
                      ? <CheckCircle className="h-4 w-4" style={{ color: '#34d399' }} />
                      : <XCircle className="h-4 w-4" style={{ color: '#f87171' }} />
                    }
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate mb-1" style={{ color: '#f1f5f9' }}>
                      {queryPreview}{queryPreview.length === 80 ? '…' : ''}
                    </p>
                    <div className="flex flex-wrap items-center gap-3 text-xs" style={{ color: '#64748b' }}>
                      <span className={isApproved ? 'status-approved' : 'status-rejected'}>
                        {(report.decision || 'unknown').toUpperCase()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {report.timestamp
                          ? new Date(report.timestamp).toLocaleDateString('en-IN', {
                              day: '2-digit', month: 'short', year: 'numeric'
                            })
                          : 'Unknown date'}
                      </span>
                      <span>₹{(report.amount || 0).toLocaleString('en-IN')}</span>
                      <span>Confidence: {confidence}</span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={() => setSelectedReport(report)}
                    className="btn-secondary text-xs py-1.5 px-3"
                  >
                    <Eye className="h-3.5 w-3.5" /> View
                  </button>
                  <button
                    onClick={() => handleExportReport(report.id)}
                    className="btn-secondary text-xs py-1.5 px-3"
                  >
                    <Download className="h-3.5 w-3.5" /> Export
                  </button>
                </div>
              </div>
            </motion.div>
          );
        })}

        {filteredReports.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <FileText className="h-14 w-14 mx-auto mb-4" style={{ color: '#1e293b' }} />
            <p className="text-base font-medium mb-1" style={{ color: '#334155' }}>
              No audit reports found
            </p>
            <p className="text-sm" style={{ color: '#475569' }}>
              Analyze a claim to generate your first report
            </p>
          </motion.div>
        )}
      </div>

      {/* Detail Modal */}
      <AnimatePresence>
        {selectedReport && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 flex items-center justify-center z-50 px-4"
            style={{ background: 'rgba(2, 6, 23, 0.85)', backdropFilter: 'blur(8px)' }}
            onClick={(e) => { if (e.target === e.currentTarget) setSelectedReport(null); }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.92, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.92, y: 20 }}
              className="card max-w-3xl w-full max-h-[88vh] overflow-y-auto"
              style={{ background: 'rgba(15,23,42,0.98)' }}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold" style={{ color: '#f1f5f9' }}>
                  Audit Report Detail
                </h2>
                <button
                  onClick={() => setSelectedReport(null)}
                  className="p-2 rounded-xl transition-colors"
                  style={{ color: '#64748b' }}
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="space-y-5">
                <div>
                  <p className="text-xs font-semibold mb-1" style={{ color: '#475569' }}>QUERY</p>
                  <p className="text-sm leading-relaxed" style={{ color: '#94a3b8' }}>
                    {selectedReport.query || 'N/A'}
                  </p>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  {[
                    { label: 'Decision', value: selectedReport.decision?.toUpperCase(), isDecision: true },
                    { label: 'Amount',   value: `₹${(selectedReport.amount || 0).toLocaleString('en-IN')}` },
                    { label: 'Confidence', value: `${((selectedReport.confidence_score || 0) * 100).toFixed(1)}%` },
                  ].map(({ label, value, isDecision }) => (
                    <div key={label}
                      className="rounded-xl p-4 text-center"
                      style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(99,102,241,0.1)' }}>
                      <p className="text-xs mb-2" style={{ color: '#475569' }}>{label}</p>
                      {isDecision
                        ? <span className={selectedReport.decision === 'approved' ? 'status-approved' : 'status-rejected'}>{value}</span>
                        : <p className="text-lg font-bold" style={{ color: '#f1f5f9' }}>{value}</p>
                      }
                    </div>
                  ))}
                </div>

                {selectedReport.justification && (
                  <div>
                    <p className="text-xs font-semibold mb-2" style={{ color: '#475569' }}>JUSTIFICATION</p>
                    <p className="text-sm leading-relaxed" style={{ color: '#94a3b8' }}>
                      {selectedReport.justification}
                    </p>
                  </div>
                )}

                {selectedReport.retrieved_chunks?.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold mb-2" style={{ color: '#475569' }}>RELEVANT CLAUSES</p>
                    <div className="space-y-2">
                      {selectedReport.retrieved_chunks.slice(0, 4).map((chunk, i) => (
                        <div key={i}
                          className="text-xs rounded-xl p-3 leading-relaxed"
                          style={{ background: 'rgba(99,102,241,0.05)', border: '1px solid rgba(99,102,241,0.1)', color: '#94a3b8' }}>
                          <strong style={{ color: '#818cf8' }}>Clause {i + 1}: </strong>
                          {typeof chunk === 'string' ? chunk : JSON.stringify(chunk)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex justify-end gap-3 pt-4 border-t" style={{ borderColor: 'rgba(99,102,241,0.15)' }}>
                  <button
                    onClick={() => { handleExportReport(selectedReport.id); setSelectedReport(null); }}
                    className="btn-primary text-sm"
                  >
                    <Download className="h-4 w-4" /> Export JSON
                  </button>
                  <button onClick={() => window.print()} className="btn-secondary text-sm">
                    <Printer className="h-4 w-4" /> Print
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AuditReports;
