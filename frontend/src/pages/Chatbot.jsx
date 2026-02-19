import React, { useState, useEffect, useRef } from 'react';
import { chatAPI } from '../services/api';
import { Send, Loader2, Bot, User, Sparkles } from 'lucide-react';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadModelInfo();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadModelInfo = async () => {
    try {
      const response = await chatAPI.getModelInfo();
      setModelInfo(response.data.model_info);
    } catch (error) {
      console.error('Error loading model info:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage({
        message: input,
        session_id: sessionId,
      });

      const { response: aiResponse, session_id, intent, confidence, metadata } = response.data;

      if (!sessionId) {
        setSessionId(session_id);
      }

      const assistantMessage = {
        role: 'assistant',
        content: aiResponse,
        intent,
        confidence,
        metadata,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setSessionId(null);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-slate-800 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Bot className="text-white" size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">AI Assistant</h2>
              <p className="text-sm text-gray-400">
                {modelInfo?.is_loaded
                  ? `Powered by ${modelInfo.model_name}`
                  : 'Loading model...'}
              </p>
            </div>
          </div>
          <button
            onClick={startNewChat}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
          >
            New Chat
          </button>
        </div>
      </div>

      {/* Chat messages */}
      <div className="flex-1 bg-slate-800 rounded-lg overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
                <Sparkles className="text-white" size={32} />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">
                Start a Conversation
              </h3>
              <p className="text-gray-400 max-w-md">
                Ask me anything! I'm here to help with information, answer questions, and have meaningful conversations.
              </p>
              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
                {[
                  'What can you help me with?',
                  'Tell me about AI and machine learning',
                  'How does natural language processing work?',
                  'What are your capabilities?',
                ].map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => setInput(suggestion)}
                    className="px-4 py-3 bg-slate-700 hover:bg-slate-600 text-gray-300 rounded-lg text-sm transition-colors text-left"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-3 animate-fade-in ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Bot className="text-white" size={18} />
                    </div>
                  )}
                  
                  <div
                    className={`max-w-[80%] md:max-w-[70%] rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : message.isError
                        ? 'bg-red-500/10 border border-red-500 text-red-400'
                        : 'bg-slate-700 text-gray-100'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    {message.role === 'assistant' && !message.isError && (
                      <div className="mt-2 pt-2 border-t border-slate-600 flex items-center gap-4 text-xs text-gray-400">
                        <span>Intent: {message.intent}</span>
                        <span>Confidence: {(message.confidence * 100).toFixed(0)}%</span>
                        {message.metadata?.has_context && (
                          <span className="text-primary-400">Context-aware</span>
                        )}
                      </div>
                    )}
                  </div>

                  {message.role === 'user' && (
                    <div className="w-8 h-8 bg-primary-700 rounded-lg flex items-center justify-center flex-shrink-0">
                      <User className="text-white" size={18} />
                    </div>
                  )}
                </div>
              ))}
              
              {loading && (
                <div className="flex gap-3 animate-fade-in">
                  <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Bot className="text-white" size={18} />
                  </div>
                  <div className="bg-slate-700 rounded-lg p-4">
                    <div className="typing-indicator flex gap-1">
                      <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                      <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                      <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input area */}
        <div className="border-t border-slate-700 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              disabled={loading}
              className="flex-1 px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50"
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <Loader2 className="animate-spin" size={20} />
              ) : (
                <Send size={20} />
              )}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
