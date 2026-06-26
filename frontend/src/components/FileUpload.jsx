import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, AlertCircle, Loader } from 'lucide-react';
import axios from 'axios';

// Live URL placeholder or localhost for development
const API_URL = import.meta.env.VITE_API_URL || '';

export default function FileUpload({ onUploadSuccess }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      await uploadFile(file);
    }
  };

  const handleChange = async (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      await uploadFile(file);
    }
  };

  const triggerInputClick = () => {
    fileInputRef.current.click();
  };

  const uploadFile = async (file) => {
    if (!file.name.endsWith('.pdf')) {
      setError('Invalid file type. Please upload an HDFC Bank statement in PDF format.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      onUploadSuccess(response.data);
    } catch (err) {
      console.error(err);
      const errMsg = err.response?.data?.detail || 'An error occurred while uploading the statement.';
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form 
        onDragEnter={handleDrag} 
        onSubmit={(e) => e.preventDefault()}
        className="relative"
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf"
          onChange={handleChange}
          disabled={loading}
        />
        
        <div
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={loading ? undefined : triggerInputClick}
          className={`group cursor-pointer border-2 border-dashed rounded-3xl p-10 flex flex-col items-center justify-center min-h-[300px] text-center transition-all duration-300 ${
            isDragActive 
              ? 'border-primary-500 bg-primary-50/50 dark:bg-primary-950/20' 
              : 'border-slate-300 dark:border-slate-800 hover:border-primary-400 bg-white/50 dark:bg-slate-900/50 hover:bg-white dark:hover:bg-slate-900 shadow-sm'
          }`}
        >
          {loading ? (
            <div className="flex flex-col items-center gap-4">
              <Loader className="w-12 h-12 text-primary-500 animate-spin" />
              <div className="space-y-1">
                <p className="text-lg font-semibold text-slate-700 dark:text-slate-200">Analyzing Statement...</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">Extracting columns, verifying balances, and running categorizations.</p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-4">
              <div className="p-4 bg-primary-50 dark:bg-primary-950/40 rounded-2xl group-hover:scale-110 transition-transform duration-300">
                <UploadCloud className="w-10 h-10 text-primary-500 dark:text-primary-400" />
              </div>
              
              <div className="space-y-1">
                <p className="text-lg font-semibold text-slate-700 dark:text-slate-200">
                  Upload HDFC PDF Statement
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Drag and drop your file here, or click to browse
                </p>
              </div>
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-2">
                Supported bank: HDFC Bank. Zero dropped transactions guaranteed.
              </p>
            </div>
          )}
        </div>
      </form>
      
      {error && (
        <div className="mt-4 p-4 rounded-2xl bg-red-50 dark:bg-red-950/30 border border-red-200/50 dark:border-red-900/30 flex items-start gap-3 text-red-700 dark:text-red-300 animate-in fade-in slide-in-from-top-4 duration-300">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <p className="font-semibold text-sm">Parsing Failed</p>
            <p className="text-xs opacity-90 leading-relaxed">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
}
