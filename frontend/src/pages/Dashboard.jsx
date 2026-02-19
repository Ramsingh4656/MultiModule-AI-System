import React, { useState, useEffect } from 'react';
import { analyticsAPI } from '../services/api';
import { FileText, Shield, FileEdit, MessageSquare, TrendingUp, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [usageData, setUsageData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [dashboardRes, usageRes] = await Promise.all([
        analyticsAPI.getDashboard(),
        analyticsAPI.getUsageByModule(),
      ]);

      setStats(dashboardRes.data.stats);
      setUsageData(usageRes.data.usage_by_module);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const modules = [
    {
      name: 'Resume Analyzer',
      icon: FileText,
      count: stats?.resume_analyses || 0,
      color: 'from-blue-500 to-cyan-500',
      path: '/resume',
    },
    {
      name: 'Spam Detector',
      icon: Shield,
      count: stats?.spam_checks || 0,
      color: 'from-red-500 to-pink-500',
      path: '/spam',
    },
    {
      name: 'Summarizer',
      icon: FileEdit,
      count: stats?.summaries_created || 0,
      color: 'from-green-500 to-emerald-500',
      path: '/summary',
    },
    {
      name: 'AI Chatbot',
      icon: MessageSquare,
      count: stats?.chat_messages || 0,
      color: 'from-purple-500 to-indigo-500',
      path: '/chat',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div className="bg-gradient-to-r from-primary-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome to AI Productivity Suite</h1>
        <p className="text-primary-100">
          Your all-in-one platform for AI-powered automation and productivity
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {modules.map((module) => {
          const Icon = module.icon;
          return (
            <div
              key={module.name}
              className="bg-slate-800 rounded-lg p-6 hover:bg-slate-750 transition-colors cursor-pointer"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 bg-gradient-to-br ${module.color} rounded-lg flex items-center justify-center`}>
                  <Icon className="text-white" size={24} />
                </div>
                <TrendingUp className="text-green-500" size={20} />
              </div>
              <h3 className="text-gray-400 text-sm mb-1">{module.name}</h3>
              <p className="text-3xl font-bold text-white">{module.count}</p>
            </div>
          );
        })}
      </div>

      {/* Usage chart */}
      <div className="bg-slate-800 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Activity size={24} />
          Module Usage
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={usageData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="module" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: '#fff',
              }}
            />
            <Bar dataKey="count" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Quick actions */}
      <div className="bg-slate-800 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {modules.map((module) => {
            const Icon = module.icon;
            return (
              <a
                key={module.name}
                href={module.path}
                className="flex items-center gap-3 p-4 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
              >
                <div className={`w-10 h-10 bg-gradient-to-br ${module.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
                  <Icon className="text-white" size={20} />
                </div>
                <span className="text-white font-medium">{module.name}</span>
              </a>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
