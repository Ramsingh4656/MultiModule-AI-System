import React, { useState } from 'react';
import { summaryAPI } from '../services/api';
import { FileEdit, Loader2 } from 'lucide-react';

const Summary = () => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSummarize = async () => {
    if (!text.trim() || text.length < 100) {
      alert('Please enter at least 100 characters of text');
      return;
    }

    setLoading(true);
    try {
      const response = await summaryAPI.create({ text, summary_ratio: 0.3 });
      setResult(response.data);
    } catch (error) {
      console.error('Error creating summary:', error);
      alert(error.response?.data?.detail || 'Error creating summary. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-slate-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
          <FileEdit size={28} />
          Text Summarizer
        </h2>
        <p className="text-gray-400 mb-6">
          Generate concise summaries from long text using AI-powered extractive summarization
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Text to Summarize (minimum 100 characters)
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste your text here..."
              rows={12}
              className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
            />
            <p className="text-sm text-gray-400 mt-2">
              Characters: {text.length} {text.length < 100 && '(minimum 100 required)'}
            </p>
          </div>

          <button
            onClick={handleSummarize}
            disabled={!text.trim() || text.length < 100 || loading}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading && <Loader2 className="animate-spin" size={20} />}
            {loading ? 'Summarizing...' : 'Generate Summary'}
          </button>
        </div>
      </div>

      {result && (
        <div className="bg-slate-800 rounded-lg p-6 animate-fade-in">
          <h3 className="text-xl font-bold text-white mb-4">Summary Results</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-slate-700 rounded-lg p-4">
              <p className="text-gray-400 text-sm mb-1">Original Length</p>
              <p className="text-2xl font-bold text-white">{result.metrics.original_length}</p>
            </div>
            <div className="bg-slate-700 rounded-lg p-4">
              <p className="text-gray-400 text-sm mb-1">Summary Length</p>
              <p className="text-2xl font-bold text-white">{result.metrics.summary_length}</p>
            </div>
            <div className="bg-slate-700 rounded-lg p-4">
              <p className="text-gray-400 text-sm mb-1">Compression</p>
              <p className="text-2xl font-bold text-white">
                {(result.metrics.compression_ratio * 100).toFixed(0)}%
              </p>
            </div>
          </div>

          <div className="space-y-6">
            <div>
              <h4 className="text-lg font-semibold text-white mb-3">Summary</h4>
              <div className="bg-slate-700 rounded-lg p-4">
                <p className="text-gray-200 leading-relaxed">{result.summary}</p>
              </div>
            </div>

            <div>
              <h4 className="text-lg font-semibold text-white mb-3">Key Points</h4>
              <ul className="space-y-2">
                {result.bullet_points.map((point, index) => (
                  <li key={index} className="flex items-start gap-3 bg-slate-700 rounded-lg p-3">
                    <span className="text-primary-500 font-bold mt-1">{index + 1}.</span>
                    <span className="text-gray-200 flex-1">{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            {result.key_terms && result.key_terms.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-white mb-3">Key Terms</h4>
                <div className="flex flex-wrap gap-2">
                  {result.key_terms.map((term, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-primary-500/20 text-primary-300 rounded-full text-sm"
                    >
                      {term}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Summary;
