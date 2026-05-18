import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
  TrendingUp,
  Clock,
  Send,
  RefreshCw,
  X,
  CheckCircle,
} from 'lucide-react';
import api from '../apiClient';
import toast from 'react-hot-toast';

const TYPE_META = {
  correction:      { label: 'Correction',   color: '#f87171', bg: 'rgba(239,68,68,0.12)',  border: 'rgba(239,68,68,0.25)'  },
  improvement:     { label: 'Improvement',  color: '#fbbf24', bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.25)' },
  bug_report:      { label: 'Bug Report',   color: '#60a5fa', bg: 'rgba(96,165,250,0.12)', border: 'rgba(96,165,250,0.25)' },
  feature_request: { label: 'Feature Req.', color: '#a78bfa', bg: 'rgba(167,139,250,0.12)',border: 'rgba(167,139,250,0.25)'},
  general:         { label: 'General',      color: '#94a3b8', bg: 'rgba(148,163,184,0.12)',border: 'rgba(148,163,184,0.25)'},
};

const FeedbackDashboard = () => {
  const [feedback, setFeedback] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedFeedback, setSelectedFeedback] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [newFeedback, setNewFeedback] = useState({
    type: 'correction',
    comment: '',
    decision_id: '',
  });

  const fetchFeedback = async () => {
    try {
      const response = await api.get('/api/feedback');
      setFeedback(Array.isArray(response.data) ? response.data : []);
    } catch {
      toast.error('Failed to load feedback');
      setFeedback([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/api/feedback/analytics');
      setAnalytics(response.data);
    } catch {
      // silently fail — analytics are optional
    }
  };

  useEffect(() => {
    fetchFeedback();
    fetchAnalytics();
  }, []);

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    if (!newFeedback.comment.trim()) {
      toast.error('Please enter a comment');
      return;
    }
    setSubmitting(true);
    try {
      await api.post('/api/feedback', {
        type: newFeedback.type,
        comment: newFeedback.comment,
        decision_id: newFeedback.decision_id || 'general',
        user_id: 'web_user',
      });
      setNewFeedback({ type: 'correction', comment: '', decision_id: '' });
      await fetchFeedback();
      await fetchAnalytics();
      toast.success('Feedback submitted — thank you!', { icon: '✅' });
    } catch {
      toast.error('Failed to submit feedback');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <div className="spinner" />
        <p className="text-sm" style={{ color: '#64748b' }}>Loading feedback…</p>
      </div>
    );
  }

  const totalFeedback  = analytics?.total_feedback  ?? feedback.length;
  const correctionRate = analytics?.correction_rate  ?? 0;
  const decisionChanges = analytics?.decision_changes ?? 0;
  const byType = analytics?.feedback_by_type ?? {};

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <MessageSquare className="h-6 w-6" style={{ color: '#818cf8' }} />
            <h1 className="page-title">Feedback Dashboard</h1>
          </div>
          <p className="page-subtitle">Human-in-the-loop corrections and system improvement requests</p>
        </div>
        <button onClick={() => { fetchFeedback(); fetchAnalytics(); }} className="btn-secondary text-sm">
          <RefreshCw className="h-4 w-4" /> Refresh
        </button>
      </div>

      {/* Analytics Overview */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { icon: MessageSquare, label: 'Total Feedback',    value: totalFeedback,                    color: '#818cf8' },
          { icon: TrendingUp,    label: 'Correction Rate',   value: `${(correctionRate*100).toFixed(1)}%`, color: '#f87171' },
          { icon: CheckCircle,   label: 'Decision Changes',  value: decisionChanges,                  color: '#34d399' },
          { icon: ThumbsDown,    label: 'Improvements Req.', value: byType.improvement ?? 0,          color: '#fbbf24' },
        ].map(({ icon: Icon, label, value, color }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="card"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium mb-2" style={{ color: '#64748b' }}>{label}</p>
                <p className="text-3xl font-black" style={{ color }}>{value}</p>
              </div>
              <div className="w-9 h-9 rounded-xl flex items-center justify-center"
                style={{ background: `${color}18`, border: `1px solid ${color}30` }}>
                <Icon className="h-4 w-4" style={{ color }} />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Submit Form */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <h3 className="text-base font-semibold mb-5" style={{ color: '#f1f5f9' }}>
            Submit Feedback
          </h3>
          <form onSubmit={handleSubmitFeedback} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: '#64748b' }}>
                  Type
                </label>
                <select
                  value={newFeedback.type}
                  onChange={(e) => setNewFeedback((p) => ({ ...p, type: e.target.value }))}
                  className="input-field"
                  style={{ appearance: 'none' }}
                >
                  {Object.entries(TYPE_META).map(([k, m]) => (
                    <option key={k} value={k}>{m.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: '#64748b' }}>
                  Decision ID (optional)
                </label>
                <input
                  type="text"
                  placeholder="report_id…"
                  value={newFeedback.decision_id}
                  onChange={(e) => setNewFeedback((p) => ({ ...p, decision_id: e.target.value }))}
                  className="input-field"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium mb-1.5" style={{ color: '#64748b' }}>
                Comment <span style={{ color: '#f87171' }}>*</span>
              </label>
              <textarea
                value={newFeedback.comment}
                onChange={(e) => setNewFeedback((p) => ({ ...p, comment: e.target.value }))}
                placeholder="Describe your feedback in detail…"
                rows={5}
                className="input-field resize-none"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="btn-primary w-full justify-center"
            >
              {submitting
                ? <><RefreshCw className="h-4 w-4 animate-spin" /> Submitting…</>
                : <><Send className="h-4 w-4" /> Submit Feedback</>
              }
            </button>
          </form>
        </motion.div>

        {/* Feedback List */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h3 className="text-base font-semibold mb-4" style={{ color: '#f1f5f9' }}>
            Recent Submissions ({feedback.length})
          </h3>
          <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
            {feedback.map((item, i) => {
              const meta = TYPE_META[item.type] || TYPE_META.general;
              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.06 }}
                  className="card cursor-pointer"
                  style={{ padding: '0.875rem 1rem' }}
                  onClick={() => setSelectedFeedback(item)}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span
                          className="text-xs font-bold px-2 py-0.5 rounded-full"
                          style={{ background: meta.bg, color: meta.color, border: `1px solid ${meta.border}` }}
                        >
                          {meta.label}
                        </span>
                        <span className="flex items-center gap-1 text-xs" style={{ color: '#475569' }}>
                          <Clock className="h-3 w-3" />
                          {item.timestamp
                            ? new Date(item.timestamp).toLocaleDateString('en-IN', {
                                day: '2-digit', month: 'short',
                              })
                            : 'N/A'}
                        </span>
                      </div>
                      <p className="text-sm truncate" style={{ color: '#94a3b8' }}>
                        {item.comment || 'No comment provided'}
                      </p>
                      {item.original_decision && (
                        <p className="text-xs mt-1" style={{ color: '#475569' }}>
                          Original: <span style={{ color: '#94a3b8' }}>{item.original_decision}</span>
                          {item.corrected_decision && (
                            <span>
                              {' '}→ <span style={{ color: '#34d399' }}>{item.corrected_decision}</span>
                            </span>
                          )}
                        </p>
                      )}
                    </div>
                    <MessageSquare className="h-4 w-4 flex-shrink-0 mt-1" style={{ color: '#334155' }} />
                  </div>
                </motion.div>
              );
            })}

            {feedback.length === 0 && (
              <div className="text-center py-16">
                <MessageSquare className="h-12 w-12 mx-auto mb-3" style={{ color: '#1e293b' }} />
                <p className="text-sm font-medium mb-1" style={{ color: '#334155' }}>No feedback yet</p>
                <p className="text-xs" style={{ color: '#475569' }}>
                  Submit the form to get started
                </p>
              </div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Detail Modal */}
      <AnimatePresence>
        {selectedFeedback && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 flex items-center justify-center z-50 px-4"
            style={{ background: 'rgba(2,6,23,0.85)', backdropFilter: 'blur(8px)' }}
            onClick={(e) => { if (e.target === e.currentTarget) setSelectedFeedback(null); }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.92, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.92, y: 20 }}
              className="card max-w-xl w-full"
              style={{ background: 'rgba(15,23,42,0.98)' }}
            >
              <div className="flex items-center justify-between mb-5">
                <h2 className="text-base font-bold" style={{ color: '#f1f5f9' }}>Feedback Detail</h2>
                <button onClick={() => setSelectedFeedback(null)} style={{ color: '#64748b' }}>
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="space-y-4">
                {[
                  { label: 'Type',      value: TYPE_META[selectedFeedback.type]?.label || selectedFeedback.type },
                  { label: 'Comment',   value: selectedFeedback.comment },
                  { label: 'User ID',   value: selectedFeedback.user_id || 'anonymous' },
                  { label: 'Timestamp', value: selectedFeedback.timestamp ? new Date(selectedFeedback.timestamp).toLocaleString() : 'N/A' },
                ].map(({ label, value }) => (
                  <div key={label}>
                    <p className="text-xs font-semibold mb-1" style={{ color: '#475569' }}>{label.toUpperCase()}</p>
                    <p className="text-sm" style={{ color: '#94a3b8' }}>{value}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FeedbackDashboard;
