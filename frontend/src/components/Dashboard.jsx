import React, { useState } from 'react';
import { 
  ArrowLeft, Download, CreditCard, Landmark, Calendar, 
  TrendingUp, TrendingDown, Layers, Percent, Briefcase, Zap 
} from 'lucide-react';
import { 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip as RechartsTooltip, Legend, PieChart, Pie, Cell 
} from 'recharts';
import axios from 'axios';
import LedgerTable from './LedgerTable';

const API_URL = import.meta.env.VITE_API_URL || '';

const PIE_COLORS = [
  '#1B365D', '#0EA5E9', '#10B981', '#F59E0B', '#EF4444', 
  '#8B5CF6', '#EC4899', '#14B8A6', '#6366F1', '#A855F7',
  '#F43F5E', '#10B981', '#84CC16', '#06B6D4', '#84CC16', '#64748B'
];

export default function Dashboard({ data, onBack, onUpdateData }) {
  const [activeTab, setActiveTab] = useState('overview');
  const { statement, transactions, analytics } = data;
  const [exporting, setExporting] = useState(false);

  // Formatting helpers
  const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(val || 0);
  };

  const handleCategoryUpdate = async (txId, newCategory) => {
    try {
      const response = await axios.put(`${API_URL}/api/transactions/${txId}/category`, {
        category: newCategory
      });
      // Update parent state
      onUpdateData({
        ...data,
        transactions: response.data.transactions,
        analytics: response.data.analytics
      });
    } catch (err) {
      console.error('Failed to update category:', err);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const response = await axios.get(`${API_URL}/api/statements/${statement.id}/export`, {
        responseType: 'blob'
      });
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const safeFilename = statement.filename.replace('.pdf', '').replace(' ', '_');
      link.setAttribute('download', `${safeFilename}_analysis.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export Excel:', err);
    } finally {
      setExporting(false);
    }
  };

  // Process data for category charts
  const categoryChartData = Object.entries(analytics.category_summary || {})
    .map(([name, vals]) => ({
      name,
      value: vals.debit,
      credit: vals.credit,
      count: vals.count
    }))
    .filter(item => item.value > 0)
    .sort((a, b) => b.value - a.value);

  // Process data for monthly inflow/outflow
  const monthlyFlowData = (analytics.monthly_flow || []).map(flow => ({
    month: flow.month,
    Inflow: flow.inflow,
    Outflow: flow.outflow
  }));

  const netCashFlow = statement.total_credits_amount - statement.total_debits_amount;

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-primary-500 dark:text-slate-400 dark:hover:text-slate-200 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Upload Another Statement</span>
        </button>
        
        <button
          onClick={handleExport}
          disabled={exporting}
          className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-primary-500 hover:bg-primary-600 disabled:bg-slate-400 text-white text-sm font-bold shadow-md shadow-primary-500/10 hover:shadow-primary-500/25 transition-all focus:outline-none"
        >
          <Download className="w-4 h-4" />
          <span>{exporting ? 'Generating Excel...' : 'Export to Excel (.xlsx)'}</span>
        </button>
      </div>

      {/* File Identifier Card */}
      <div className="p-6 glass-panel flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-primary-50 dark:bg-primary-950/40 rounded-2xl">
            <CreditCard className="w-6 h-6 text-primary-500" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">{statement.filename}</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">HDFC Bank • Account ending in {statement.account_number?.slice(-4) || 'XXXX'}</p>
          </div>
        </div>
        
        <div className="flex flex-wrap items-center gap-6 text-sm">
          <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
            <Landmark className="w-4 h-4 text-slate-400" />
            <span>Branch: <span className="font-semibold text-slate-800 dark:text-slate-200">{statement.branch || 'N/A'}</span></span>
          </div>
          <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
            <Calendar className="w-4 h-4 text-slate-400" />
            <span>Period: <span className="font-semibold text-slate-800 dark:text-slate-200">{statement.start_date} to {statement.end_date}</span></span>
          </div>
        </div>
      </div>

      {/* Tabs Selector */}
      <div className="flex border-b border-slate-200 dark:border-slate-800">
        {[
          { id: 'overview', label: 'Account Overview' },
          { id: 'ledger', label: 'Transaction Ledger' },
          { id: 'analytics', label: 'Analytics & Summary' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-6 py-3.5 text-sm font-bold border-b-2 -mb-px transition-all focus:outline-none ${
              activeTab === tab.id
                ? 'border-primary-500 text-primary-500 dark:text-primary-400 font-extrabold'
                : 'border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tabs Content */}
      <div className="space-y-6">
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* KPI Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
              <div className="p-6 glass-panel flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Opening Balance</p>
                  <p className="text-2xl font-extrabold text-slate-800 dark:text-slate-100 mt-2">{formatCurrency(statement.opening_balance)}</p>
                </div>
              </div>
              <div className="p-6 glass-panel flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Closing Balance</p>
                  <p className="text-2xl font-extrabold text-slate-800 dark:text-slate-100 mt-2">{formatCurrency(statement.closing_balance)}</p>
                </div>
              </div>
              <div className="p-6 glass-panel flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Deposits (CR)</p>
                  <p className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-2">{formatCurrency(statement.total_credits_amount)}</p>
                  <p className="text-xs text-slate-400 mt-1">{statement.total_credits_count} credit transactions</p>
                </div>
                <TrendingUp className="w-8 h-8 text-emerald-500/20" />
              </div>
              <div className="p-6 glass-panel flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Withdrawals (DR)</p>
                  <p className="text-2xl font-extrabold text-red-600 dark:text-red-400 mt-2">{formatCurrency(statement.total_debits_amount)}</p>
                  <p className="text-xs text-slate-400 mt-1">{statement.total_debits_count} debit transactions</p>
                </div>
                <TrendingDown className="w-8 h-8 text-red-500/20" />
              </div>
            </div>

            {/* Inflow vs Outflow Visual & Info Summary */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Monthly Trend Chart */}
              <div className="p-6 glass-panel lg:col-span-2 space-y-4">
                <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200">Monthly Inflow vs Outflow</h3>
                <div className="h-[300px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={monthlyFlowData}
                      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" className="dark:stroke-slate-800" />
                      <XAxis dataKey="month" stroke="#94A3B8" fontSize={12} tickLine={false} />
                      <YAxis stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} />
                      <RechartsTooltip 
                        contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        formatter={(value) => formatCurrency(value)}
                      />
                      <Legend iconType="circle" />
                      <Bar dataKey="Inflow" fill="#10B981" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Outflow" fill="#EF4444" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Net flow overview details */}
              <div className="p-6 glass-panel flex flex-col justify-between">
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200">Net Flow Analysis</h3>
                  <div className={`p-4 rounded-2xl flex flex-col gap-1 ${
                    netCashFlow >= 0 
                      ? 'bg-emerald-50 text-emerald-800 dark:bg-emerald-950/20 dark:text-emerald-400' 
                      : 'bg-red-50 text-red-800 dark:bg-red-950/20 dark:text-red-400'
                  }`}>
                    <span className="text-xs font-semibold uppercase tracking-wider opacity-85">Net Cash Flow</span>
                    <span className="text-3xl font-black">{formatCurrency(netCashFlow)}</span>
                    <span className="text-xs opacity-90 mt-1">
                      {netCashFlow >= 0 
                        ? 'Congratulations! You spent less than you received this statement period.' 
                        : 'Warning: Your spending exceeded your total inflows for this period.'}
                    </span>
                  </div>
                </div>
                
                <div className="space-y-3 mt-6 pt-4 border-t border-slate-100 dark:border-slate-800/50">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500">Account Holder</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">{statement.account_holder}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500">Account Number</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">{statement.account_number}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500">IFSC Code</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">{statement.ifsc}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* LEDGER TAB */}
        {activeTab === 'ledger' && (
          <LedgerTable 
            transactions={transactions} 
            onCategoryUpdate={handleCategoryUpdate} 
          />
        )}

        {/* ANALYTICS TAB */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Category Spending distribution */}
              <div className="p-6 glass-panel lg:col-span-2 space-y-4">
                <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200">Debit Spending by Category</h3>
                
                {categoryChartData.length > 0 ? (
                  <div className="flex flex-col md:flex-row items-center justify-around gap-6">
                    <div className="w-[200px] h-[200px] shrink-0">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={categoryChartData}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={2}
                            dataKey="value"
                          >
                            {categoryChartData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                            ))}
                          </Pie>
                          <RechartsTooltip formatter={(value) => formatCurrency(value)} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                    
                    {/* Spending Legend List */}
                    <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[220px] overflow-y-auto pr-2">
                      {categoryChartData.map((item, index) => (
                        <div key={item.name} className="flex items-center gap-2.5 text-sm">
                          <span 
                            className="w-3.5 h-3.5 rounded-full shrink-0" 
                            style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }}
                          />
                          <span className="text-slate-500 font-medium truncate flex-1">{item.name}</span>
                          <span className="font-semibold text-slate-800 dark:text-slate-200">{formatCurrency(item.value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="py-20 text-center text-slate-400 dark:text-slate-500">
                    No debit transactions to analyze.
                  </div>
                )}
              </div>

              {/* Categorization coverage rate */}
              <div className="p-6 glass-panel flex flex-col justify-between">
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200">Categorization rate</h3>
                  <div className="flex items-center justify-center py-6">
                    <div className="relative flex items-center justify-center">
                      {/* Circular Gauge */}
                      <svg className="w-32 h-32 transform -rotate-90">
                        <circle
                          cx="64"
                          cy="64"
                          r="52"
                          className="stroke-slate-200 dark:stroke-slate-800"
                          strokeWidth="10"
                          fill="transparent"
                        />
                        <circle
                          cx="64"
                          cy="64"
                          r="52"
                          className="stroke-primary-500 transition-all duration-1000 ease-out"
                          strokeWidth="10"
                          fill="transparent"
                          strokeDasharray={2 * Math.PI * 52}
                          strokeDashoffset={2 * Math.PI * 52 * (1 - analytics.percentage_categorized / 100)}
                          strokeLinecap="round"
                        />
                      </svg>
                      <div className="absolute text-center">
                        <span className="text-2xl font-black text-slate-800 dark:text-slate-100">
                          {analytics.percentage_categorized}%
                        </span>
                        <p className="text-[10px] uppercase font-bold text-slate-400 mt-0.5">Categorized</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 text-xs text-slate-400 leading-relaxed text-center">
                  <p>
                    Of {analytics.total_transactions} transactions,{' '}
                    <span className="font-semibold text-slate-600 dark:text-slate-300">
                      {Math.round(analytics.total_transactions * (analytics.percentage_categorized / 100))}
                    </span>{' '}
                    matched keyword filters.
                  </p>
                  <p>Change categories in the Ledger tab to increase coverage.</p>
                </div>
              </div>
            </div>

            {/* Recurring Patterns - Salary & EMI */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Salary Credits card */}
              <div className="p-6 glass-panel space-y-4">
                <div className="flex items-center gap-2">
                  <Briefcase className="w-5 h-5 text-emerald-500" />
                  <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200">Auto-Detected Salaries</h3>
                </div>
                
                {analytics.salaries && analytics.salaries.length > 0 ? (
                  <div className="space-y-4">
                    {analytics.salaries.map((sal, idx) => (
                      <div key={idx} className="p-4 rounded-2xl bg-emerald-50/50 dark:bg-emerald-950/10 border border-emerald-100/50 dark:border-emerald-900/10 flex items-start gap-4">
                        <div className="p-2.5 bg-emerald-100 dark:bg-emerald-950/40 rounded-xl text-emerald-700 dark:text-emerald-400">
                          <TrendingUp className="w-5 h-5" />
                        </div>
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-800 dark:text-slate-100">{formatCurrency(sal.amount)}</span>
                            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400">
                              {sal.frequency}
                            </span>
                          </div>
                          <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">{sal.pattern}</p>
                          <p className="text-[10px] text-emerald-600 dark:text-emerald-500 font-medium">Detected {sal.count} monthly occurrences</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-400 dark:text-slate-500 py-6 text-center">
                    No monthly recurring credit patterns found (approx same amount monthly).
                  </p>
                )}
              </div>

              {/* EMIs & Loans card */}
              <div className="p-6 glass-panel space-y-4">
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-amber-500" />
                  <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200">Auto-Detected EMIs & Loans</h3>
                </div>
                
                {analytics.emis && analytics.emis.length > 0 ? (
                  <div className="space-y-4 max-h-[300px] overflow-y-auto pr-1">
                    {analytics.emis.map((emi, idx) => (
                      <div key={idx} className="p-4 rounded-2xl bg-amber-50/30 dark:bg-amber-950/10 border border-amber-100/30 dark:border-amber-900/10 flex items-start gap-4">
                        <div className="p-2.5 bg-amber-100 dark:bg-amber-950/40 rounded-xl text-amber-700 dark:text-amber-400">
                          <TrendingDown className="w-5 h-5" />
                        </div>
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-800 dark:text-slate-100">{formatCurrency(emi.amount)}</span>
                            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-400">
                              {emi.frequency}
                            </span>
                          </div>
                          <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">{emi.pattern}</p>
                          <p className="text-[10px] text-amber-600 dark:text-amber-500 font-medium font-semibold">Detected {emi.count} recurring occurrences</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-400 dark:text-slate-500 py-6 text-center">
                    No recurring monthly loan or EMI debit patterns found (fixed monthly amount).
                  </p>
                )}
              </div>
            </div>

            {/* Top 5 largest transactions list */}
            <div className="p-6 glass-panel space-y-4">
              <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200">Top 5 Largest Transactions</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="bg-slate-50 dark:bg-slate-900 text-slate-400 font-bold border-b border-slate-100 dark:border-slate-800">
                      <th className="px-4 py-3">Date</th>
                      <th className="px-4 py-3">Description</th>
                      <th className="px-4 py-3 text-right">Amount</th>
                      <th className="px-4 py-3 text-center">Type</th>
                      <th className="px-4 py-3 text-center">Category</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800/50">
                    {analytics.top_5_transactions?.map((tx, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/20 dark:hover:bg-slate-900/5 transition-colors">
                        <td className="px-4 py-3 text-slate-400 whitespace-nowrap">
                          {new Date(tx.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                        </td>
                        <td className="px-4 py-3 font-medium text-slate-800 dark:text-slate-200 truncate max-w-sm">
                          {tx.description}
                        </td>
                        <td className="px-4 py-3 text-right font-bold text-slate-800 dark:text-slate-100 whitespace-nowrap">
                          {formatCurrency(tx.amount)}
                        </td>
                        <td className="px-4 py-3 text-center whitespace-nowrap">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            tx.type === 'Credit' 
                              ? 'bg-emerald-50 text-emerald-800 dark:bg-emerald-950/20 dark:text-emerald-400' 
                              : 'bg-red-50 text-red-800 dark:bg-red-950/20 dark:text-red-400'
                          }`}>
                            {tx.type}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center whitespace-nowrap">
                          <span className="text-xs bg-slate-100 text-slate-600 dark:bg-slate-850 dark:text-slate-400 px-2 py-1 rounded-full font-semibold">
                            {tx.category}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
