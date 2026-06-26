import React, { useState } from 'react';
import { Search, Filter, ArrowUpRight, ArrowDownLeft, ChevronLeft, ChevronRight, Edit2 } from 'lucide-react';

const CATEGORIES = [
  "Salary", "EMI / Loan", "Food & Dining", "Travel", "Shopping", 
  "Utilities", "Telecom", "Entertainment", "Healthcare", "Education", 
  "Investments", "Insurance", "Cash Withdrawal", "UPI / Transfer", "Rent", "Other"
];

export default function LedgerTable({ transactions, onCategoryUpdate }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [typeFilter, setTypeFilter] = useState('All');
  const [currentPage, setCurrentPage] = useState(1);
  const [editingId, setEditingId] = useState(null);
  const itemsPerPage = 15;

  // Formatting helpers
  const formatCurrency = (val) => {
    if (val === null || val === undefined || val === 0.0) return '-';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(val);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const parts = dateStr.split('-');
      if (parts.length === 3) {
        const date = new Date(parts[0], parts[1] - 1, parts[2]);
        return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: '2-digit' });
      }
      return dateStr;
    } catch {
      return dateStr;
    }
  };

  // Filtering
  const filteredTransactions = transactions.filter((tx) => {
    const matchesSearch = tx.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (tx.ref_no && tx.ref_no.toLowerCase().includes(searchTerm.toLowerCase()));
      
    const matchesCategory = categoryFilter === 'All' || tx.category === categoryFilter;
    
    let matchesType = true;
    if (typeFilter === 'Debit') {
      matchesType = tx.debit > 0;
    } else if (typeFilter === 'Credit') {
      matchesType = tx.credit > 0;
    }
    
    return matchesSearch && matchesCategory && matchesType;
  });

  // Pagination
  const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage) || 1;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedTransactions = filteredTransactions.slice(startIndex, startIndex + itemsPerPage);

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  return (
    <div className="space-y-4">
      {/* Filters Toolbar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 glass-panel">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search description or reference..."
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 border-none text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 text-slate-800 dark:text-slate-200"
          />
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={categoryFilter}
              onChange={(e) => { setCategoryFilter(e.target.value); setCurrentPage(1); }}
              className="px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 border-none text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 text-slate-800 dark:text-slate-200"
            >
              <option value="All">All Categories</option>
              {CATEGORIES.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          
          <select
            value={typeFilter}
            onChange={(e) => { setTypeFilter(e.target.value); setCurrentPage(1); }}
            className="px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 border-none text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 text-slate-800 dark:text-slate-200"
          >
            <option value="All">All Transactions</option>
            <option value="Debit">Debits (DR)</option>
            <option value="Credit">Credits (CR)</option>
          </select>
        </div>
      </div>

      {/* Ledger Grid */}
      <div className="glass-panel overflow-hidden border border-slate-200/50 dark:border-slate-800/50 rounded-2xl">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr className="bg-slate-100/50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400 font-semibold border-b border-slate-200/50 dark:border-slate-800/50">
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Narration</th>
                <th className="px-6 py-4">Ref/Chq No</th>
                <th className="px-6 py-4 text-right">Withdrawal (DR)</th>
                <th className="px-6 py-4 text-right">Deposit (CR)</th>
                <th className="px-6 py-4 text-right">Running Balance</th>
                <th className="px-6 py-4 text-center">Category</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {paginatedTransactions.length > 0 ? (
                paginatedTransactions.map((tx) => (
                  <tr 
                    key={tx.id} 
                    className="hover:bg-slate-50/50 dark:hover:bg-slate-900/20 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-slate-500 dark:text-slate-400">
                      {formatDate(tx.date)}
                    </td>
                    <td className="px-6 py-4 max-w-sm font-medium text-slate-800 dark:text-slate-200 leading-relaxed break-words">
                      {tx.description}
                    </td>
                    <td className="px-6 py-4 text-slate-400 dark:text-slate-500 whitespace-nowrap">
                      {tx.ref_no || '-'}
                    </td>
                    <td className="px-6 py-4 text-right whitespace-nowrap font-medium text-red-600 dark:text-red-400">
                      {tx.debit > 0 ? formatCurrency(tx.debit) : '-'}
                    </td>
                    <td className="px-6 py-4 text-right whitespace-nowrap font-medium text-emerald-600 dark:text-emerald-400">
                      {tx.credit > 0 ? formatCurrency(tx.credit) : '-'}
                    </td>
                    <td className="px-6 py-4 text-right whitespace-nowrap font-semibold text-slate-700 dark:text-slate-300">
                      {formatCurrency(tx.balance)}
                    </td>
                    <td className="px-6 py-4 text-center whitespace-nowrap">
                      {editingId === tx.id ? (
                        <select
                          value={tx.category}
                          autoFocus
                          onChange={(e) => {
                            onCategoryUpdate(tx.id, e.target.value);
                            setEditingId(null);
                          }}
                          onBlur={() => setEditingId(null)}
                          className="px-2 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-xs border border-primary-500 focus:outline-none text-slate-800 dark:text-slate-200"
                        >
                          {CATEGORIES.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                          ))}
                        </select>
                      ) : (
                        <button
                          onClick={() => setEditingId(tx.id)}
                          className={`group/btn px-3 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1.5 mx-auto transition-all ${
                            tx.category === 'Other'
                              ? 'bg-slate-100 hover:bg-slate-200 text-slate-500 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-400'
                              : tx.category === 'Salary'
                              ? 'bg-emerald-50 hover:bg-emerald-100 text-emerald-700 dark:bg-emerald-950/30 dark:hover:bg-emerald-950/50 dark:text-emerald-400'
                              : 'bg-primary-50 hover:bg-primary-100 text-primary-700 dark:bg-primary-950/30 dark:hover:bg-primary-950/50 dark:text-primary-400'
                          }`}
                        >
                          <span>{tx.category}</span>
                          <Edit2 className="w-3.5 h-3.5 opacity-0 group-hover/btn:opacity-100 transition-opacity text-slate-400 dark:text-slate-500" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-slate-400 dark:text-slate-500">
                    No transactions match your search or filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Toolbar */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-100/30 dark:bg-slate-900/30 border-t border-slate-200/50 dark:border-slate-800/50 text-sm">
          <p className="text-slate-500 dark:text-slate-400">
            Showing <span className="font-semibold text-slate-800 dark:text-slate-200">{filteredTransactions.length > 0 ? startIndex + 1 : 0}</span> to{' '}
            <span className="font-semibold text-slate-800 dark:text-slate-200">
              {Math.min(startIndex + itemsPerPage, filteredTransactions.length)}
            </span>{' '}
            of <span className="font-semibold text-slate-800 dark:text-slate-200">{filteredTransactions.length}</span> records
          </p>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-900 text-slate-600 dark:text-slate-400 disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-slate-700 dark:text-slate-300 font-medium">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-900 text-slate-600 dark:text-slate-400 disabled:opacity-40 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
