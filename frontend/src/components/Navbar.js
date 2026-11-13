import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  BarChart3,
  FileText,
  MessageSquare,
  FolderOpen,
  Brain,
  Menu,
  X,
  Activity,
} from 'lucide-react';

const navItems = [
  { path: '/',          label: 'Analyzer',   icon: Search      },
  { path: '/analytics', label: 'Analytics',  icon: BarChart3   },
  { path: '/audit',     label: 'Audit',      icon: FileText    },
  { path: '/feedback',  label: 'Feedback',   icon: MessageSquare },
  { path: '/documents', label: 'Documents',  icon: FolderOpen  },
];

const Navbar = () => {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [location]);

  return (
    <>
      <nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? 'backdrop-blur-xl border-b'
            : 'border-b border-transparent'
        }`}
        style={{
          background: scrolled
            ? 'rgba(10, 15, 30, 0.95)'
            : 'rgba(10, 15, 30, 0.8)',
          borderColor: scrolled ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">

            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <div
                className="w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-110"
                style={{
                  background: 'linear-gradient(135deg, #6366f1, #4ade80)',
                  boxShadow: '0 4px 15px rgba(99,102,241,0.4)',
                }}
              >
                <Brain className="h-5 w-5 text-white" />
              </div>
              <div className="leading-none">
                <p className="text-sm font-bold text-white tracking-tight">InsureClaims</p>
                <p className="text-xs" style={{ color: '#64748b' }}>AI Claim Evaluation</p>
              </div>
            </Link>

            {/* Desktop nav */}
            <div className="hidden md:flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className="relative flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200"
                    style={{
                      color: isActive ? '#818cf8' : '#64748b',
                      background: isActive ? 'rgba(99,102,241,0.1)' : 'transparent',
                    }}
                    onMouseEnter={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.color = '#94a3b8';
                        e.currentTarget.style.background = 'rgba(99,102,241,0.05)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.color = '#64748b';
                        e.currentTarget.style.background = 'transparent';
                      }
                    }}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                    {isActive && (
                      <motion.div
                        layoutId="activeTab"
                        className="absolute bottom-0 left-3 right-3 h-0.5 rounded-full"
                        style={{ background: 'linear-gradient(90deg, #6366f1, #4ade80)' }}
                        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                      />
                    )}
                  </Link>
                );
              })}
            </div>

            {/* Status indicator + Mobile button */}
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full"
                style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)' }}>
                <Activity className="h-3 w-3" style={{ color: '#34d399' }} />
                <span className="text-xs font-medium" style={{ color: '#34d399' }}>System Live</span>
              </div>

              <button
                className="md:hidden p-2 rounded-xl transition-colors"
                style={{ color: '#64748b' }}
                onClick={() => setMobileOpen(!mobileOpen)}
                aria-label="Toggle menu"
              >
                {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        <AnimatePresence>
          {mobileOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="md:hidden overflow-hidden border-t"
              style={{
                background: 'rgba(10, 15, 30, 0.98)',
                borderColor: 'rgba(99, 102, 241, 0.15)',
              }}
            >
              <div className="px-4 py-3 space-y-1">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all"
                      style={{
                        color: isActive ? '#818cf8' : '#64748b',
                        background: isActive ? 'rgba(99,102,241,0.1)' : 'transparent',
                      }}
                    >
                      <Icon className="h-4 w-4" />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* Spacer for fixed navbar */}
      <div className="h-16" />
    </>
  );
};

export default Navbar;
