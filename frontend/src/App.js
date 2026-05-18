import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import ClaimAnalyzer from './components/ClaimAnalyzer';
import Analytics from './components/Analytics';
import AuditReports from './components/AuditReports';
import FeedbackDashboard from './components/FeedbackDashboard';
import DocumentManager from './components/DocumentManager';

function App() {
  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'rgba(15, 23, 42, 0.95)',
            color: '#e2e8f0',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            backdropFilter: 'blur(12px)',
            borderRadius: '12px',
            fontSize: '14px',
            fontFamily: 'Inter, sans-serif',
          },
          success: {
            iconTheme: { primary: '#34d399', secondary: 'rgba(15,23,42,0.95)' },
          },
          error: {
            iconTheme: { primary: '#f87171', secondary: 'rgba(15,23,42,0.95)' },
          },
        }}
      />
      <Navbar />
      <motion.main
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4 }}
        className="max-w-7xl mx-auto px-4 sm:px-6 py-8"
      >
        <Routes>
          <Route path="/"          element={<ClaimAnalyzer />}    />
          <Route path="/analytics" element={<Analytics />}         />
          <Route path="/audit"     element={<AuditReports />}      />
          <Route path="/feedback"  element={<FeedbackDashboard />} />
          <Route path="/documents" element={<DocumentManager />}   />
        </Routes>
      </motion.main>
    </>
  );
}

export default App;
