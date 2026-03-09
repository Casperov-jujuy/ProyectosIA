'use client';

import { useState, useRef } from 'react';
import { Upload, FileText, Check, Download, Share2, X, Loader2, Briefcase } from 'lucide-react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'completed'>('idle');
  const [progress, setProgress] = useState(0);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loadingStep, setLoadingStep] = useState(0); // 0: Analyzing, 1: Matching, 2: Formatting

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile);
      } else {
        alert('Please upload a PDF file.');
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const simulateProgress = () => {
    // Simulate steps progress visually while waiting for backend
    let currentProgress = 0;
    const interval = setInterval(() => {
      currentProgress += Math.random() * 5;
      if (currentProgress > 90) {
        currentProgress = 90; // Hold at 90 until actual response
      }
      setProgress(Math.floor(currentProgress));

      if (currentProgress < 30) setLoadingStep(0);
      else if (currentProgress < 60) setLoadingStep(1);
      else setLoadingStep(2);

    }, 500);
    return interval;
  };

  const handleSubmit = async () => {
    if (!file || !jobDescription) return;

    setStatus('processing');
    const intervalId = simulateProgress();

    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDescription);

    try {
      const response = await fetch('http://localhost:8000/api/optimize', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown server error' }));
        throw new Error(errorData.detail || 'Optimization failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      setPdfUrl(url);

      clearInterval(intervalId);
      setProgress(100);
      setStatus('completed');
    } catch (err: unknown) {
      console.error(err);
      clearInterval(intervalId);
      setStatus('idle');
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      alert(`Error: ${errorMessage}`);
    }
  };

  const reset = () => {
    setFile(null);
    setJobDescription('');
    setStatus('idle');
    setProgress(0);
    setPdfUrl(null);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-sans selection:bg-blue-500/30">

      {/* Header */}
      <header className="p-6 flex items-center justify-between border-b border-white/10">
        <div className="flex items-center gap-2">
          {/* Simple Logo Placeholder */}
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <span className="font-semibold text-lg tracking-tight">CV Optimizer</span>
        </div>
      </header>

      <main className="max-w-md mx-auto p-6 flex flex-col gap-6">

        {/* Main Interface when Idle */}
        {(status === 'idle' || status === 'uploading') && (
          <>
            <div className="text-center space-y-2 py-4">
              <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                Optimize your CV for ATS
              </h1>
              <p className="text-gray-400 text-sm">
                Upload your CV and enter your target job to begin the Harvard-style optimization.
              </p>
            </div>

            {/* Upload Zone */}
            <div
              className={`
                border-2 border-dashed rounded-2xl p-8 transition-all duration-300 ease-in-out
                flex flex-col items-center justify-center gap-4 cursor-pointer text-center group
                ${isDragging ? 'border-blue-500 bg-blue-500/10' : 'border-white/10 hover:border-white/20 hover:bg-white/5'}
                ${file ? 'bg-blue-900/10 border-blue-500' : ''}
              `}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept=".pdf"
                className="hidden"
              />

              <div className={`p-4 rounded-full transition-colors ${file ? 'bg-blue-600' : 'bg-white/5 group-hover:bg-white/10'}`}>
                {file ? <Check className="w-8 h-8 text-white" /> : <Upload className="w-8 h-8 text-blue-400" />}
              </div>

              <div className="space-y-1">
                <h3 className="font-medium text-lg">
                  {file ? file.name : 'Upload CV (PDF)'}
                </h3>
                <p className="text-xs text-gray-500">
                  {file ? 'Click to change file' : 'Tap to select or drag and drop your file here'}
                </p>
              </div>

              {file && (
                <span className="px-3 py-1 bg-blue-600/20 text-blue-300 text-xs rounded-full font-medium">Ready</span>
              )}
            </div>

            {/* Job Description Input */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300 ml-1">Target Job Position</label>
              <div className="relative">
                <textarea
                  className="w-full bg-[#121212] border border-white/10 rounded-xl p-4 text-sm text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-600/50 focus:border-blue-600 transition-all resize-none h-32"
                  placeholder="e.g. Senior Product Manager at Google..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                />
                <Briefcase className="absolute bottom-4 right-4 w-4 h-4 text-gray-600" />
              </div>
              <p className="text-xs text-gray-500 px-1">
                Our AI uses this role to align your experience with Harvard&apos;s standard action-oriented keywords.
              </p>
            </div>

            {/* Action Button */}
            <button
              onClick={handleSubmit}
              disabled={!file || !jobDescription}
              className={`
                w-full py-4 rounded-xl font-bold text-sm tracking-wide transition-all shadow-lg
                flex items-center justify-center gap-2
                ${(!file || !jobDescription)
                  ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/20 hover:shadow-blue-600/40'}
              `}
            >
              Optimize My CV
            </button>
          </>
        )}

        {/* Processing State Overlay */}
        {status === 'processing' && (
          <div className="fixed inset-0 z-50 bg-[#0a0a0a] flex flex-col items-center justify-center p-6 animate-in fade-in duration-300">
            <div className="w-full max-w-sm space-y-8 text-center">

              {/* Visual Circle Loader placeholder */}
              <div className="relative w-40 h-40 mx-auto flex items-center justify-center">
                <div className="absolute inset-0 border-4 border-dashed border-blue-900 rounded-full animate-[spin_10s_linear_infinite]"></div>
                <div className="absolute inset-0 border-4 border-t-blue-500 border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
                <span className="text-3xl font-bold font-mono">{progress}%</span>
              </div>

              <div className="space-y-2">
                <h2 className="text-2xl font-bold">AI is refining your CV</h2>
                <p className="text-gray-400 text-sm">Matching your experience with top-tier ATS requirements and Harvard formatting standards.</p>
              </div>

              {/* Steps List */}
              <div className="bg-[#121212] rounded-xl p-4 space-y-3 text-left border border-white/5">
                <StepItem label="Analyzing CV components" done={loadingStep > 0} active={loadingStep === 0} />
                <StepItem label="Matching with job requirements" done={loadingStep > 1} active={loadingStep === 1} />
                <StepItem label="Formatting to Harvard Standard" done={loadingStep > 2} active={loadingStep === 2} />
              </div>

              <button onClick={() => setStatus('idle')} className="text-sm text-gray-500 hover:text-white transition-colors">
                Cancel Optimization
              </button>
            </div>
          </div>
        )}

        {/* Completed State */}
        {status === 'completed' && pdfUrl && (
          <div className="fixed inset-0 z-50 bg-[#0a0a0a] flex flex-col overflow-hidden animate-in slide-in-from-bottom duration-500">

            {/* Header for result */}
            <div className="p-4 flex items-center justify-between border-b border-white/10 bg-[#0a0a0a]/80 backdrop-blur-md sticky top-0 z-10">
              <button onClick={reset} className="p-2 hover:bg-white/10 rounded-full">
                <X className="w-5 h-5" />
              </button>
              <h3 className="font-semibold">Optimized CV</h3>
              <span className="text-blue-500 text-sm font-medium cursor-not-allowed opacity-50">Edit</span>
            </div>

            {/* Preview Area */}
            <div className="flex-1 bg-[#151515] p-4 lg:p-8 overflow-y-auto flex justify-center">
              <div className="w-full max-w-2xl bg-white shadow-2xl min-h-[800px] relative animate-in zoom-in-95 duration-300">
                <iframe src={pdfUrl} className="w-full h-full absolute inset-0" title="PDF Preview" />
              </div>
            </div>

            {/* Bottom Action Bar */}
            <div className="p-6 border-t border-white/10 bg-[#0a0a0a] space-y-4">

              <div className="flex items-center justify-between px-2">
                <div className="flex flex-col">
                  <span className="text-blue-500 font-bold text-3xl">95</span>
                  <span className="text-xs text-gray-500 uppercase tracking-wider">ATS Score</span>
                </div>
                <p className="text-xs text-gray-400 max-w-[200px] text-right">
                  Excellent! Your CV is highly optimized for recruitment software.
                </p>
              </div>

              <div className="flex gap-3">
                <a
                  href={pdfUrl}
                  download="optimized_cv.pdf"
                  className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-transform active:scale-95"
                >
                  <Download className="w-5 h-5" />
                  Download PDF
                </a>
                <button className="p-4 bg-[#1a1a1a] hover:bg-[#2a2a2a] rounded-xl text-white transition-colors">
                  <Share2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

function StepItem({ label, done, active }: { label: string, done: boolean, active: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div className={`w-5 h-5 rounded-full flex items-center justify-center border ${done ? 'bg-blue-600 border-blue-600' : active ? 'border-blue-500' : 'border-gray-600'}`}>
        {done && <Check className="w-3 h-3 text-white" />}
        {active && <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />}
      </div>
      <span className={`text-sm ${done || active ? 'text-white' : 'text-gray-500'}`}>{label}</span>
      {done && <span className="ml-auto text-[10px] font-bold text-blue-500">DONE</span>}
      {active && <span className="ml-auto text-[10px] font-bold text-blue-400 animate-pulse">...</span>}
    </div>
  );
}
