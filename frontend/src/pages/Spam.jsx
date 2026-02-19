import React, { useState } from 'react';
import { spamAPI } from '../services/api';
import { Shield, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';

const Spam = () => {
  const [emailText, setEmailText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleCheck = async () => {
    if (!emailText.trim()) return;

    setLoading(true);
    try {
      const response = await spamAPI.check({ email_text: emailText });
      setResult(response.data);
    } catch (error) {
      console.error('Error checking spam:', error);
      alert('Error checking email. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'HIGH':
        return 'text-red-500 bg-red-500/10 border-red-500';
      case 'MEDIUM':
        return 'text-yellow-500 bg-yellow-500/10 border-yellow-500';
      case 'LOW':
        return 'text-green-500 bg-green-500/10 border-green-500';
      default:
        return 'text-gray-500 bg-gray-500/10 border-gray-500';
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-slate-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
          <Shield size={28} />
          Spam & Phishing Detector
        </h2>
        <p className="text-gray-400 mb-6">
          Analyze email content to detect spam and phishing attempts
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Email Content
            </label>
            <textarea
              value={emailText}
              onChange={(e) => setEmailText(e.target.value)}
              placeholder="Paste email content here..."
              rows={8}
              className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
            />
          </div>

          <button
            onClick={handleCheck}
            disabled={!emailText.trim() || loading}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading && <Loader2 className="animate-spin" size={20} />}
            {loading ? 'Analyzing...' : 'Check Email'}
          </button>
        </div>
      </div>

      {result && (
        <div className="bg-slate-800 rounded-lg p-6 animate-fade-in">
          <h3 className="text-xl font-bold text-white mb-4">Analysis Results</h3>
          
          <div className={`border-2 rounded-lg p-6 mb-6 ${getRiskColor(result.risk_level)}`}>
            <div className="flex items-center gap-3 mb-4">
              {result.is_spam ? (
                <AlertTriangle size={32} />
              ) : (
                <CheckCircle size={32} />
              )}
              <div>
                <h4 className="text-2xl font-bold">{result.classification}</h4>
                <p className="text-sm opacity-80">Risk Level: {result.risk_level}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div>
                <p className="text-sm opacity-80">Confidence</p>
                <p className="text-2xl font-bold">{(result.confidence * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h4 className="text-lg font-semibold text-white mb-2">Detection Reasons</h4>
              <ul className="space-y-2">
                {result.reasons.map((reason, index) => (
                  <li key={index} className="flex items-start gap-2 text-gray-300">
                    <span className="text-primary-500 mt-1">•</span>
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-700 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">Spam Keywords</p>
                <p className="text-2xl font-bold text-white">{result.features.spam_keywords}</p>
              </div>
              <div className="bg-slate-700 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">Phishing Patterns</p>
                <p className="text-2xl font-bold text-white">{result.features.phishing_patterns}</p>
              </div>
              <div className="bg-slate-700 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">Risk Level</p>
                <p className={`text-2xl font-bold ${getRiskColor(result.risk_level).split(' ')[0]}`}>
                  {result.risk_level}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Spam;
