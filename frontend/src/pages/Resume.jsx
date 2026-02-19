import React, { useState } from 'react';
import { resumeAPI } from '../services/api';
import { Upload, FileText, CheckCircle, XCircle, Loader2 } from 'lucide-react';

const Resume = () => {
  const [file, setFile] = useState(null);
  const [requiredSkills, setRequiredSkills] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    if (requiredSkills) {
      formData.append('required_skills', requiredSkills);
    }

    try {
      const response = await resumeAPI.analyze(formData);
      setResult(response.data);
    } catch (error) {
      console.error('Error analyzing resume:', error);
      alert('Error analyzing resume. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-slate-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
          <FileText size={28} />
          Resume Analyzer
        </h2>
        <p className="text-gray-400 mb-6">
          Upload a resume to extract skills and match against requirements
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Upload Resume (PDF or TXT)
            </label>
            <div className="flex items-center gap-4">
              <label className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-slate-700 border-2 border-dashed border-slate-600 rounded-lg cursor-pointer hover:bg-slate-600 transition-colors">
                <Upload size={20} className="text-gray-400" />
                <span className="text-gray-300">
                  {file ? file.name : 'Choose file'}
                </span>
                <input
                  type="file"
                  accept=".pdf,.txt"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Required Skills (comma-separated, optional)
            </label>
            <input
              type="text"
              value={requiredSkills}
              onChange={(e) => setRequiredSkills(e.target.value)}
              placeholder="python, react, machine learning"
              className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading && <Loader2 className="animate-spin" size={20} />}
            {loading ? 'Analyzing...' : 'Analyze Resume'}
          </button>
        </div>
      </div>

      {result && (
        <div className="bg-slate-800 rounded-lg p-6 animate-fade-in">
          <h3 className="text-xl font-bold text-white mb-4">Analysis Results</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-slate-700 rounded-lg p-4">
              <p className="text-gray-400 text-sm mb-1">Match Score</p>
              <p className="text-3xl font-bold text-white">{result.match_score}%</p>
            </div>
            <div className="bg-slate-700 rounded-lg p-4">
              <p className="text-gray-400 text-sm mb-1">Skills Found</p>
              <p className="text-3xl font-bold text-white">{result.total_skills_found}</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h4 className="text-lg font-semibold text-white mb-2">Skills Found</h4>
              <div className="space-y-2">
                {Object.entries(result.skills_found).map(([category, skills]) => (
                  <div key={category} className="bg-slate-700 rounded-lg p-3">
                    <p className="text-primary-400 font-medium capitalize mb-2">{category}</p>
                    <div className="flex flex-wrap gap-2">
                      {skills.map((skill, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-slate-600 text-gray-200 rounded-full text-sm"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {result.missing_skills && result.missing_skills.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Missing Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {result.missing_skills.map((skill, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm"
                    >
                      {skill}
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

export default Resume;
