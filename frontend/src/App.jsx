import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Resume from './pages/Resume';
import Spam from './pages/Spam';
import Summary from './pages/Summary';
import Chatbot from './pages/Chatbot';
import Analytics from './pages/Analytics';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/resume" element={<Resume />} />
          <Route path="/spam" element={<Spam />} />
          <Route path="/summary" element={<Summary />} />
          <Route path="/chat" element={<Chatbot />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
