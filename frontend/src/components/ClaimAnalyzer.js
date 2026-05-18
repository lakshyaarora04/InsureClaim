import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  Brain,
  TrendingUp,
  Eye,
  Download,
  MessageSquare,
  RefreshCw,
  Zap,
  Shield,
  ChevronRight,
  Sparkles,
  AlertTriangle,
} from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../apiClient';

const SAMPLE_QUERIES = [
  "I'm a 45-year-old male who needs cataract surgery in Pune. My policy is 24 months old.",
  "A 32-year-old female needs emergency knee surgery after a road accident. Policy active for 18 months.",
  "I'm a 55-year-old male requiring cardiac bypass surgery in Mumbai. Policy is 36 months old.",
  "A 28-year-old female needs hospitalization for appendicitis in Delhi. Policy started 8 months ago.",
];

const ConfidenceGauge = ({ score }) => {
  const pct = Math.round((score || 0) * 100);
  const color = pct >= 70 ? '#34d399' : pct >= 50 ? '#fbbf24' : '#f87171';
  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-24 h-24">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(99,102,241,0.15)" strokeWidth="8" />
          <circle
            cx="50" cy="50" r="40" fill="none"
            stroke={color} strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xl font-bold" style={{ color }}>{pct}%</span>
        </div>
      </div>
      <p className="text-xs mt-1" style={{ color: '#64748b' }}>Confidence</p>
    </div>
  );
};

const ClaimAnalyzer = () => {
  const [query, setQuery] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [showReasoningTree, setShowReasoningTree] = useState(false);

  const handleAnalyze = async () => {
    if (!query.trim()) {
      toast.error('Please describe the insurance claim first.');
      return;
    }
    setIsAnalyzing(true);
    setAnalysisResult(null);
    try {
      const response = await api.post('/api/analyze', { query });
      setAnalysisResult(response.data);
      toast.success('Analysis complete!', { icon: '🧠' });
    } catch (error) {
      const msg = error.response?.data?.detail || 'Analysis failed. Please try again.';
      toast.error(msg);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setQuery('');
    setAnalysisResult(null);
    setShowReasoningTree(false);
  };

  const handleOverride = async (newDecision) => {
    if (!analysisResult) return;
    try {
      await api.post('/api/feedback', {
        type: 'correction',
        original_decision: analysisResult.decision,
        corrected_decision: newDecision,
        comment: 'Manual override by adjuster',
        user_id: 'web_user',
      });
      setAnalysisResult((prev) => ({
        ...prev,
        decision: newDecision,
        override_reason: 'Manual correction by adjuster',
      }));
      toast.success(`Decision overridden to ${newDecision.toUpperCase()}`);
    } catch {
      toast.error('Failed to override decision');
    }
  };

  const handleExportAudit = async () => {
    if (!analysisResult) return;
    try {
      const blob = new Blob([JSON.stringify(analysisResult, null, 2)], {
        type: 'application/json',
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_report_${Date.now()}.json`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success('Audit report exported!');
    } catch {
      toast.error('Failed to export audit report');
    }
  };

  const isApproved = analysisResult?.decision === 'approved';

  return (
    <div className="page-container">
      {/* ── Hero Section ─────────────────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center mb-12"
      >
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-6 text-sm font-medium"
          style={{
            background: 'rgba(99,102,241,0.1)',
            border: '1px solid rgba(99,102,241,0.3)',
            color: '#818cf8',
          }}>
          <Sparkles className="h-3.5 w-3.5" />
          Powered by LLM + RAG Pipeline
        </div>

        <h1 className="text-5xl font-black mb-4 leading-tight">
          <span className="gradient-text">AI-Powered</span>{' '}
          <span style={{ color: '#f1f5f9' }}>Insurance</span>
          <br />
          <span style={{ color: '#f1f5f9' }}>Claim Analyzer</span>
        </h1>
        <p className="text-lg max-w-2xl mx-auto" style={{ color: '#64748b' }}>
          Submit a claim description in plain English. Our AI evaluates it against
          uploaded policy documents using semantic retrieval + LLM reasoning.
        </p>

        {/* Stat pills */}
        <div className="flex justify-center gap-4 mt-8 flex-wrap">
          {[
            { icon: Shield, label: '96.8% Accuracy', color: '#34d399' },
            { icon: Zap,    label: '<2s Response',   color: '#818cf8' },
            { icon: Brain,  label: 'LLM Reasoning',  color: '#f472b6' },
          ].map(({ icon: Icon, label, color }) => (
            <div key={label}
              className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium"
              style={{ background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(99,102,241,0.15)', color }}>
              <Icon className="h-4 w-4" />
              {label}
            </div>
          ))}
        </div>
      </motion.div>

      {/* ── Input Card ───────────────────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card-premium mb-6"
      >
        <div className="flex items-center gap-2 mb-4">
          <Search className="h-5 w-5" style={{ color: '#818cf8' }} />
          <h2 className="text-base font-semibold" style={{ color: '#f1f5f9' }}>
            Claim Description
          </h2>
        </div>

        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe the insurance claim in natural language…&#10;e.g. 'I'm a 45-year-old male who needs cataract surgery in Pune. My policy is 24 months old.'"
          rows={4}
          className="input-field resize-none mb-4 leading-relaxed"
          style={{ fontSize: '0.9rem' }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleAnalyze();
          }}
        />

        {/* Quick-fill samples */}
        <div className="mb-5">
          <p className="text-xs mb-2" style={{ color: '#475569' }}>
            Quick examples — click to fill:
          </p>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_QUERIES.map((sq, i) => (
              <button
                key={i}
                onClick={() => setQuery(sq)}
                className="text-xs px-3 py-1.5 rounded-lg transition-all"
                style={{
                  background: 'rgba(99,102,241,0.08)',
                  border: '1px solid rgba(99,102,241,0.2)',
                  color: '#818cf8',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(99,102,241,0.15)';
                  e.currentTarget.style.borderColor = 'rgba(99,102,241,0.4)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(99,102,241,0.08)';
                  e.currentTarget.style.borderColor = 'rgba(99,102,241,0.2)';
                }}
              >
                Example {i + 1}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="btn-primary flex-1"
          >
            {isAnalyzing ? (
              <><RefreshCw className="h-4 w-4 animate-spin" /> Analyzing…</>
            ) : (
              <><Brain className="h-4 w-4" /> Analyze Claim</>
            )}
          </button>
          <button onClick={handleClear} className="btn-secondary">
            Clear
          </button>
        </div>

        {isAnalyzing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 flex items-center gap-3 text-sm"
            style={{ color: '#64748b' }}
          >
            <div className="flex gap-1">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-2 h-2 rounded-full"
                  style={{ background: '#6366f1' }}
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ repeat: Infinity, duration: 1.2, delay: i * 0.4 }}
                />
              ))}
            </div>
            Retrieving relevant policy clauses via semantic search…
          </motion.div>
        )}
      </motion.div>

      {/* ── Results Card ─────────────────────────────────────────────────────── */}
      <AnimatePresence>
        {analysisResult && (
          <motion.div
            key="result"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 24 }}
            transition={{ duration: 0.5 }}
            className="card-premium"
            style={isApproved
              ? { borderColor: 'rgba(16,185,129,0.3)', boxShadow: '0 0 30px rgba(16,185,129,0.1)' }
              : { borderColor: 'rgba(239,68,68,0.3)',  boxShadow: '0 0 30px rgba(239,68,68,0.1)' }
            }
          >
            {/* Decision header */}
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <div
                  className="w-12 h-12 rounded-2xl flex items-center justify-center"
                  style={{
                    background: isApproved ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                    border: `1px solid ${isApproved ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`,
                  }}
                >
                  {isApproved
                    ? <CheckCircle className="h-6 w-6" style={{ color: '#34d399' }} />
                    : <XCircle className="h-6 w-6" style={{ color: '#f87171' }} />
                  }
                </div>
                <div>
                  <p className="text-xs font-medium mb-1" style={{ color: '#64748b' }}>Decision</p>
                  <span className={isApproved ? 'status-approved' : 'status-rejected'} style={{ fontSize: '1rem', fontWeight: 700 }}>
                    {analysisResult.decision?.toUpperCase()}
                  </span>
                </div>
              </div>
              <ConfidenceGauge score={analysisResult.confidence_score} />
            </div>

            {/* Key metrics grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              {[
                {
                  label: 'Coverage Amount',
                  value: `₹${(analysisResult.amount || 0).toLocaleString('en-IN')}`,
                  color: '#818cf8',
                },
                {
                  label: 'Claim Type',
                  value: analysisResult.query_data?.procedure || 'Medical',
                  color: '#60a5fa',
                },
                {
                  label: 'Accident Case',
                  value: analysisResult.query_data?.accident ? 'Yes' : 'No',
                  color: '#fbbf24',
                },
                {
                  label: 'Response Time',
                  value: analysisResult.response_time_ms
                    ? `${analysisResult.response_time_ms}ms`
                    : 'N/A',
                  color: '#34d399',
                },
              ].map(({ label, value, color }) => (
                <div
                  key={label}
                  className="rounded-xl p-4 text-center"
                  style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(99,102,241,0.1)' }}
                >
                  <p className="text-xs mb-1" style={{ color: '#475569' }}>{label}</p>
                  <p className="font-bold text-sm" style={{ color }}>{value}</p>
                </div>
              ))}
            </div>

            <hr className="divider" />

            {/* Justification */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <Brain className="h-4 w-4" style={{ color: '#818cf8' }} />
                <h3 className="text-sm font-semibold" style={{ color: '#f1f5f9' }}>AI Justification</h3>
              </div>
              <p className="text-sm leading-relaxed" style={{ color: '#94a3b8' }}>
                {analysisResult.justification || 'No justification available.'}
              </p>
            </div>

            {/* Waiting Period / Reasoning Breakdown */}
            {analysisResult.reasoning_breakdown && (
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <Clock className="h-4 w-4" style={{ color: '#818cf8' }} />
                  <h3 className="text-sm font-semibold" style={{ color: '#f1f5f9' }}>Waiting Period Analysis</h3>
                </div>
                <div
                  className="rounded-xl p-4 text-sm leading-relaxed"
                  style={{ background: 'rgba(15,23,42,0.6)', color: '#94a3b8', border: '1px solid rgba(99,102,241,0.1)' }}
                >
                  {analysisResult.reasoning_breakdown}
                </div>
              </div>
            )}

            {/* Relevant Clauses */}
            {analysisResult.retrieved_chunks?.length > 0 && (
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <FileText className="h-4 w-4" style={{ color: '#818cf8' }} />
                  <h3 className="text-sm font-semibold" style={{ color: '#f1f5f9' }}>Relevant Policy Clauses</h3>
                </div>
                <div className="space-y-2">
                  {analysisResult.retrieved_chunks.slice(0, 3).map((chunk, i) => (
                    <div
                      key={i}
                      className="rounded-xl p-3 text-xs leading-relaxed"
                      style={{ background: 'rgba(99,102,241,0.05)', border: '1px solid rgba(99,102,241,0.1)', color: '#94a3b8' }}
                    >
                      <span className="font-semibold" style={{ color: '#818cf8' }}>Clause {i + 1}: </span>
                      {chunk.substring(0, 180)}…
                    </div>
                  ))}
                </div>
              </div>
            )}

            <hr className="divider" />

            {/* Action buttons */}
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => setShowReasoningTree(!showReasoningTree)}
                className="btn-secondary text-sm"
              >
                <Eye className="h-4 w-4" />
                {showReasoningTree ? 'Hide' : 'Show'} Reasoning Tree
              </button>
              <button
                onClick={() => handleOverride(isApproved ? 'rejected' : 'approved')}
                className="btn-secondary text-sm"
              >
                <AlertTriangle className="h-4 w-4" />
                Override to {isApproved ? 'Rejected' : 'Approved'}
              </button>
              <button onClick={handleExportAudit} className="btn-secondary text-sm">
                <Download className="h-4 w-4" />
                Export Audit JSON
              </button>
            </div>

            {/* Reasoning Tree */}
            <AnimatePresence>
              {showReasoningTree && analysisResult.reasoning_tree && (
                <motion.div
                  key="tree"
                  initial={{ opacity: 0, height: 0, marginTop: 0 }}
                  animate={{ opacity: 1, height: 'auto', marginTop: 16 }}
                  exit={{ opacity: 0, height: 0, marginTop: 0 }}
                  className="rounded-xl p-4 overflow-hidden"
                  style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(99,102,241,0.15)' }}
                >
                  <h4 className="text-sm font-semibold mb-4 flex items-center gap-2" style={{ color: '#f1f5f9' }}>
                    <TrendingUp className="h-4 w-4" style={{ color: '#818cf8' }} />
                    Step-by-Step Reasoning
                  </h4>
                  <div className="space-y-3">
                    {analysisResult.reasoning_tree.steps?.map((step, i) => (
                      <div key={i} className="flex items-start gap-3">
                        <div
                          className="w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center mt-0.5"
                          style={{
                            background: step.status ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)',
                            border: `1px solid ${step.status ? 'rgba(16,185,129,0.4)' : 'rgba(239,68,68,0.4)'}`,
                          }}
                        >
                          {step.status
                            ? <CheckCircle className="h-3 w-3" style={{ color: '#34d399' }} />
                            : <XCircle className="h-3 w-3" style={{ color: '#f87171' }} />
                          }
                        </div>
                        <div>
                          <p className="text-xs font-semibold" style={{ color: '#e2e8f0' }}>{step.title}</p>
                          <p className="text-xs" style={{ color: '#64748b' }}>{step.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ClaimAnalyzer;
