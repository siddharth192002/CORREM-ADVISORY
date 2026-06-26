import React, { useState, useEffect } from 'react';
import { Landmark, FileText, Calendar, Trash2, Eye, TrendingUp, Sparkles } from 'lucide-react';
import axios from 'axios';

import FileUpload from './components/FileUpload';
import Dashboard from './components/Dashboard';
import ThemeToggle from './components/ThemeToggle';

const API_URL = import.meta.env.VITE_API_URL || '';

export default function App() {
  const [activeStatementData, setActiveStatementData] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Fetch statements upload history on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/statements`);
      setHistory(response.data);
    } catch (err) {
      console.error('Failed to fetch upload history:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleUploadSuccess = async (statement) => {
    // When uploaded successfully, load its full detail
    await loadStatementDetails(statement.id);
    fetchHistory(); // refresh history list
  };

  const loadStatementDetails = async (id) => {
    try {
      const response = await axios.get(`${API_URL}/api/statements/${id}`);
      setActiveStatementData(response.data);
    } catch (err) {
      console.error('Failed to load statement details:', err);
    }
  };

  const handleDeleteStatement = async (id, e) => {
    e.stopPropagation(); // stop click from triggering list selection
    if (window.confirm('Are you sure you want to delete this statement and its transactions?')) {
      try {
        await axios.delete(`${API_URL}/api/statements/${id}`);
        fetchHistory();
        if (activeStatementData?.statement.id === id) {
          setActiveStatementData(null);
        }
      } catch (err) {
        console.error('Failed to delete statement:', err);
      }
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const parts = dateStr.split('T')[0].split('-');
      if (parts.length === 3) {
        const date = new Date(parts[0], parts[1] - 1, parts[2]);
        return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
      }
      return dateStr;
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="min-h-screen pb-12 transition-colors duration-300">
      {/* Navbar Header */}
      <header className="sticky top-0 z-50 border-b border-slate-200/50 dark:border-slate-800/50 bg-white/70 dark:bg-slate-950/70 backdrop-blur-md transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-500 rounded-xl text-white shadow-md shadow-primary-500/25">
              <Landmark className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-base font-extrabold tracking-tight text-slate-800 dark:text-slate-100 flex items-center gap-1.5">
                Bank Statement Analyzer
                <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-primary-100 dark:bg-primary-950/60 text-primary-600 dark:text-primary-400">HDFC</span>
              </h1>
              <p className="text-[10px] text-slate-400 font-medium">Automatic PDF extraction, classification & Excel download</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 animate-in fade-in duration-500">
        {activeStatementData ? (
          <Dashboard 
            data={activeStatementData} 
            onBack={() => setActiveStatementData(null)}
            onUpdateData={setActiveStatementData}
          />
        ) : (
          <div className="space-y-8">
            {/* Upload Zone Section */}
            <div className="space-y-4 text-center max-w-2xl mx-auto">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary-50 dark:bg-primary-950/40 text-xs font-bold text-primary-600 dark:text-primary-400 border border-primary-200/30 dark:border-primary-800/30 shadow-sm mb-2">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Zero transaction drops guaranteed</span>
              </div>
              <h2 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100 sm:text-4xl">
                Analyze your statement in seconds
              </h2>
              <p className="text-base text-slate-500 dark:text-slate-400 max-w-lg mx-auto leading-relaxed">
                Accepts official HDFC Bank PDF statements. Parses details, validates balance chains, and categorizes transactions instantly.
              </p>
            </div>
            
            <FileUpload onUploadSuccess={handleUploadSuccess} />

            {/* Historical Uploads Grid / Table */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200">Previous Statement Analyses</h3>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
                  {history.length} statement{history.length !== 1 ? 's' : ''}
                </span>
              </div>
              
              <div className="glass-panel overflow-hidden border border-slate-200/50 dark:border-slate-800/50 rounded-2xl">
                {historyLoading ? (
                  <div className="text-center py-12 text-slate-400 dark:text-slate-500">
                    Loading upload history...
                  </div>
                ) : history.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead>
                        <tr className="bg-slate-100/50 dark:bg-slate-900/50 text-slate-400 font-semibold border-b border-slate-200/50 dark:border-slate-800/50">
                          <th className="px-6 py-4">Filename</th>
                          <th className="px-6 py-4">Holder Name</th>
                          <th className="px-6 py-4">Account Number</th>
                          <th className="px-6 py-4">Period</th>
                          <th className="px-6 py-4">Uploaded At</th>
                          <th className="px-6 py-4 text-center">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                        {history.map((stmt) => (
                          <tr 
                            key={stmt.id} 
                            onClick={() => loadStatementDetails(stmt.id)}
                            className="hover:bg-slate-50/50 dark:hover:bg-slate-900/20 cursor-pointer transition-colors"
                          >
                            <td className="px-6 py-4 font-bold text-slate-700 dark:text-slate-200 flex items-center gap-2">
                              <FileText className="w-4 h-4 text-primary-500 shrink-0" />
                              <span className="truncate max-w-xs">{stmt.filename}</span>
                            </td>
                            <td className="px-6 py-4 text-slate-500 dark:text-slate-400 font-medium">
                              {stmt.account_holder}
                            </td>
                            <td className="px-6 py-4 text-slate-400 dark:text-slate-500">
                              {stmt.account_number}
                            </td>
                            <td className="px-6 py-4 text-slate-600 dark:text-slate-300 font-medium whitespace-nowrap">
                              <Calendar className="w-3.5 h-3.5 inline mr-1 text-slate-400" />
                              {stmt.start_date} to {stmt.end_date}
                            </td>
                            <td className="px-6 py-4 text-slate-400 dark:text-slate-500">
                              {formatDate(stmt.uploaded_at)}
                            </td>
                            <td className="px-6 py-4 text-center">
                              <div className="flex items-center justify-center gap-2">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    loadStatementDetails(stmt.id);
                                  }}
                                  className="p-1.5 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-950/30 text-slate-400 hover:text-primary-500 transition-colors"
                                  title="View Report"
                                >
                                  <Eye className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={(e) => handleDeleteStatement(stmt.id, e)}
                                  className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/30 text-slate-400 hover:text-red-500 transition-colors"
                                  title="Delete Record"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-16 text-slate-400 dark:text-slate-500 space-y-2">
                    <p className="font-semibold text-slate-600 dark:text-slate-350">No statements uploaded yet</p>
                    <p className="text-xs">Statements you upload will be stored here in SQLite for historical tracking.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
