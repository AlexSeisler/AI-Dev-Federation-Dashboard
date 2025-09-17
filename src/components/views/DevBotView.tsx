import React, { useState, useEffect, useRef } from 'react';
import { Bot, Play, Terminal, FileText, Package, AlertCircle, Copy, CheckCircle, Clock, X, Lightbulb } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface Task {
  id: number;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  context?: string;
  logs: LogEntry[];
}

interface LogEntry {
  event: string;
  timestamp: string;
}

const taskPresets = [
  { 
    id: 'brainstorm', 
    name: 'Alignment/Plan', 
    description: 'Strategic planning and brainstorming',
    needsRepo: false,
    needsFile: false
  },
  { 
    id: 'structure', 
    name: 'Structure Analysis', 
    description: 'Analyze repository structure and architecture',
    needsRepo: true,
    needsFile: false
  },
  { 
    id: 'file', 
    name: 'File Analysis', 
    description: 'Deep dive analysis of specific files',
    needsRepo: true,
    needsFile: true
  },
];

const API_URL = import.meta.env.VITE_API_URL;

if (!API_URL) {
  throw new Error("❌ VITE_API_URL is not set. Please configure it in your Netlify environment.");
}

export const DevBotView: React.FC = () => {
  const { user } = useAuth();
  const [selectedPreset, setSelectedPreset] = useState<string>('');
  const [repoId, setRepoId] = useState('AlexSeisler/AI-Dev-Federation-Dashboard');
  const [filePath, setFilePath] = useState('src/App.tsx');
  const [userPrompt, setUserPrompt] = useState('Analyze this project and suggest improvements');
  const [isRunning, setIsRunning] = useState(false);
  const [currentTask, setCurrentTask] = useState<Task | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [output, setOutput] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [showColdStartMessage, setShowColdStartMessage] = useState(false);
  const [showOnboardingBanner, setShowOnboardingBanner] = useState(true);
  const [lastTaskResult, setLastTaskResult] = useState<string>('');
  
  const logConsoleRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Auto-scroll logs
  useEffect(() => {
    if (logConsoleRef.current) {
      logConsoleRef.current.scrollTop = logConsoleRef.current.scrollHeight;
    }
  }, [logs]);

  // Cleanup EventSource on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const getToken = () => localStorage.getItem('access_token');
  const refreshToken = async (expiredToken: string): Promise<string | null> => {
    try {
      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: expiredToken }),
      });

      if (!response.ok) {
        console.error("Token refresh failed:", await response.text());
        return null;
      }

      const data = await response.json();
      localStorage.setItem("access_token", data.access_token);
      console.log("🔄 Token refreshed");
      return data.access_token;
    } catch (err) {
      console.error("Refresh request error:", err);
      return null;
    }
  };

  const fetchWithAuth = async (url: string, options: RequestInit = {}): Promise<Response> => {
    let token = getToken();
    if (!token) throw new Error("No token available");

    // Refresh if expired
    if (isTokenExpired(token)) {
      console.warn("JWT expired — refreshing before API call...");
      const newToken = await refreshToken(token);
      if (!newToken) throw new Error("Session expired, please log in again");
      token = newToken;
    }

    const authHeaders = {
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`,
    };

    const response = await fetch(url, { ...options, headers: authHeaders });

    // Handle unauthorized → try refresh once
    if (response.status === 401) {
      console.warn("401 received — trying token refresh...");
      const newToken = await refreshToken(token);
      if (!newToken) throw new Error("Session expired, please log in again");

      return fetch(url, {
        ...options,
        headers: { ...authHeaders, Authorization: `Bearer ${newToken}` },
      });
    }

    return response;
  };

  const validateInputs = (preset: string): string | null => {
    const presetConfig = taskPresets.find(p => p.id === preset);
    if (!presetConfig) return 'Invalid preset selected';

    if (presetConfig.needsRepo && !repoId.trim()) {
      return `${presetConfig.name} requires a repository ID (owner/repo format)`;
    }

    if (presetConfig.needsFile && !filePath.trim()) {
      return `${presetConfig.name} requires a file path`;
    }

    if (preset === 'brainstorm' && !userPrompt.trim()) {
      return 'Alignment/Plan requires a prompt or question';
    }

    return null;
  };

  const buildRequestBody = (preset: string) => {
    const presetConfig = taskPresets.find(p => p.id === preset);
    if (!presetConfig) return {};

    const body: any = {};

    if (preset === 'brainstorm') {
      body.context = userPrompt;
    } else {
      const contextData: any = {};
      if (presetConfig.needsRepo) contextData.repo_id = repoId;
      if (presetConfig.needsFile) contextData.file_path = filePath;
      body.context = contextData;
    }

    return body;
  };

  const startTask = async () => {
    if (!selectedPreset) {
      setError('Please select a task preset');
      return;
    }

    const validationError = validateInputs(selectedPreset);
    if (validationError) {
      setError(validationError);
      return;
    }

    const token = getToken();
    if (!token) {
      setError('Authentication required. Please sign up or log in.');
      return;
    }

    if (user?.status === 'pending') {
      console.log('User is pending — running in demo mode.');
    } else if (!user) {
      setError('Authentication required. Please log in.');
      return;
    }

    setIsRunning(true);
    setError('');
    setLogs([]);
    setOutput('');
    setCurrentTask(null);

    try {
      const requestBody = buildRequestBody(selectedPreset);
      
      const response = await fetchWithAuth(`${API_URL}/tasks/run/${selectedPreset}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        if (response.status === 503 || response.status === 502) {
          setShowColdStartMessage(true);
          setTimeout(() => setShowColdStartMessage(false), 5000);
          throw new Error('⚡ Backend waking up (cold start). Please retry in a few seconds.');
        }
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const taskId = data.task_id;

      // ✅ Always fetch token fresh for SSE
      streamTaskLogs(taskId);

    } catch (err) {
      console.error('Task start failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to start task');
      setIsRunning(false);
    }
  };

  function isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.exp * 1000 < Date.now();
    } catch (e) {
      console.error("Invalid JWT:", e);
      return true;
    }
  }

  const streamTaskLogs = async (taskId: number) => {
    setOutput("");
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    let token = getToken();
    if (!token) {
      setError("No token available. Please log in again.");
      setIsRunning(false);
      return;
    }

    if (isTokenExpired(token)) {
      console.warn("JWT expired — attempting refresh...");
      const newToken = await refreshToken(token);
      if (!newToken) {
        setError("Session expired. Please log in again.");
        setIsRunning(false);
        return;
      }
      token = newToken;
    }

    const eventSource = new EventSource(`${API_URL}/tasks/${taskId}/stream?token=${token}`);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      console.log("🔥 SSE message:", event.data);
      try {
        const data = JSON.parse(event.data);
        setLogs((prev) => [...prev, data]);
      } catch {
        setLogs((prev) => [
          ...prev,
          { event: event.data, timestamp: new Date().toISOString() },
        ]);
      }
    };

    eventSource.onerror = () => {
      console.error("SSE error");
      eventSource.close();
      fetchTaskResult(taskId);
    };

    setTimeout(() => {
      if (eventSource.readyState === EventSource.OPEN) {
        eventSource.close();
        fetchTaskResult(taskId);
      }
    }, 30000);
  };

  const fetchTaskResult = async (taskId: number) => {
    try {
      const response = await fetchWithAuth(`${API_URL}/tasks/${taskId}`);
      if (response.ok) {
        const task = await response.json();
        setCurrentTask(task);
        setLogs(task.logs || []);
        
        // Store last result for quick replay
        if (task.output) {
          setLastTaskResult(task.output);
        }

        // ✅ Use full response from backend
        if (task.output) {
          setOutput(task.output);
        } else {
          // fallback for old tasks
          const outputLog = [...(task.logs || [])].reverse().find(
            (log: LogEntry) => log.event.includes('HF Response:')
          );
          if (outputLog) {
            const clean = outputLog.event.split('HF Response:')[1]?.trim();
            setOutput(clean || outputLog.event);
          }
        }

        setIsRunning(false);
      }
    } catch (err) {
      console.error('Failed to fetch task result:', err);
      setIsRunning(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  const selectedPresetConfig = taskPresets.find(p => p.id === selectedPreset);
  const isFormValid = selectedPreset && (
    selectedPreset === 'brainstorm' ? userPrompt.trim() : 
    selectedPresetConfig?.needsRepo ? repoId.trim() && (!selectedPresetConfig.needsFile || filePath.trim()) :
    true
  );

  return (
    <div className="h-full p-6 overflow-auto bg-slate-900/20">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-gradient-to-br from-green-500/20 to-blue-500/20 rounded-xl border border-green-500/30">
              <Bot className="w-8 h-8 text-green-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">DevBot Console</h1>
              <p className="text-green-300">Interactive Development Assistant</p>
            </div>
          </div>

          {showColdStartMessage && (
            <div className="mb-4 p-4 bg-orange-900/20 border border-orange-500/30 rounded-lg flex items-center gap-3">
              <Clock className="w-5 h-5 text-orange-400 animate-pulse" />
              <span className="text-orange-300">⚡ Backend waking up (cold start). Please retry in a few seconds.</span>
            </div>
          )}

          {/* Onboarding Banner */}
          {showOnboardingBanner && (
            <div className="mb-6 p-4 bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30 rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Lightbulb className="w-5 h-5 text-blue-400" />
                <div>
                  <p className="text-blue-300 font-medium">Welcome to DevBot! 🚀</p>
                  <p className="text-blue-200 text-sm">Select a task preset and run your first AI analysis. Start with Alignment/Plan for a quick brainstorm.</p>
                </div>
              </div>
              <button
                onClick={() => setShowOnboardingBanner(false)}
                className="text-blue-400 hover:text-blue-300 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          )}

          {error && (
            <div className="mb-4 p-4 bg-red-900/20 border border-red-500/30 rounded-lg flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400" />
              <span className="text-red-300">{error}</span>
            </div>
          )}
        </div>

        {/* Main Layout */}
        <div className="flex flex-col lg:grid lg:grid-cols-3 gap-6">
          {/* Control Panel */}
          <div className="w-full lg:col-span-1 space-y-6">
            {/* Step Indicator */}
            <div className="bg-slate-800/60 rounded-xl p-4 border border-slate-700/50">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-sm">
                <div className={`flex items-center gap-2 ${selectedPreset ? 'text-green-400' : 'text-blue-400'}`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${selectedPreset ? 'bg-green-500/20 border border-green-500/50' : 'bg-blue-500/20 border border-blue-500/50'}`}>
                    1
                  </div>
                  <span>Choose Task</span>
                </div>
                <div className={`flex items-center gap-2 ${selectedPreset && isFormValid ? 'text-green-400' : 'text-slate-500'}`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${selectedPreset && isFormValid ? 'bg-green-500/20 border border-green-500/50' : 'bg-slate-600/20 border border-slate-600/50'}`}>
                    2
                  </div>
                  <span>Configure</span>
                </div>
                <div className={`flex items-center gap-2 ${isFormValid ? 'text-blue-400' : 'text-slate-500'}`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${isFormValid ? 'bg-blue-500/20 border border-blue-500/50' : 'bg-slate-600/20 border border-slate-600/50'}`}>
                    3
                  </div>
                  <span>Run</span>
                </div>
              </div>
            </div>

            {/* Task Presets */}
            <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700/50">
              <h3 className="text-white font-semibold mb-3">Task Presets</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-2">
                {taskPresets.map((preset) => (
                  <button
                    key={preset.id}
                    onClick={() => setSelectedPreset(preset.id)}
                    disabled={isRunning}
                    className={`w-full text-left px-3 py-3 rounded-lg transition-all duration-200 hover:scale-[1.02] ${
                      selectedPreset === preset.id
                        ? 'bg-blue-600/30 border border-blue-500/50 text-blue-300'
                        : 'bg-slate-700/30 border border-slate-600/30 text-slate-300 hover:bg-slate-700/50 hover:border-slate-500/50'
                    } ${isRunning ? 'opacity-50 cursor-not-allowed' : ''}`}
                    style={{ minHeight: '60px' }}
                  >
                    <div className="font-medium">{preset.name}</div>
                    <div className="text-xs text-slate-400 mt-1">{preset.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Config Inputs */}
            {selectedPresetConfig && (
              <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700/50">
                <h3 className="text-white font-semibold mb-3">Configuration</h3>
                <div className="space-y-4">
                  {selectedPreset === 'brainstorm' && (
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Prompt / Question
                      </label>
                      <textarea
                        value={userPrompt}
                        onChange={(e) => setUserPrompt(e.target.value)}
                        disabled={isRunning}
                        className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                        rows={3}
                        style={{ minHeight: '80px' }}
                        placeholder="e.g., 'Analyze this project for security vulnerabilities and suggest improvements'"
                      />
                    </div>
                  )}

                  {selectedPresetConfig.needsRepo && (
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Repository ID
                      </label>
                      <input
                        type="text"
                        value={repoId}
                        onChange={(e) => setRepoId(e.target.value)}
                        disabled={isRunning}
                        className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="AlexSeisler/AI-Dev-Federation-Dashboard"
                        style={{ minHeight: '44px' }}
                      />
                    </div>
                  )}

                  {selectedPresetConfig.needsFile && (
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        File Path
                      </label>
                      <input
                        type="text"
                        value={filePath}
                        onChange={(e) => setFilePath(e.target.value)}
                        disabled={isRunning}
                        className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="src/App.tsx"
                        style={{ minHeight: '44px' }}
                      />
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Run Button */}
            <button
              onClick={startTask}
              disabled={!isFormValid || isRunning || !user}
              className={`w-full py-4 px-6 rounded-xl font-semibold transition-all duration-200 flex items-center justify-center gap-3 min-h-[56px] ${
                !isFormValid || isRunning || !user
                  ? 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
                  : user?.status === 'pending'
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg shadow-purple-500/20'
                    : 'bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white shadow-lg shadow-green-500/20'
              }`}
            >
              {isRunning ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Running...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  {user?.status === 'pending' ? 'Run Demo Task' : 'Execute Task'}
                </>
              )}
            </button>

            {!user && (
              <div className="text-center text-slate-400 text-sm">
                Please log in to run tasks
              </div>
            )}
          </div>

          {/* Logs + Output */}
          <div className="w-full lg:col-span-2 space-y-6">
            {/* Logs */}
            <div className="bg-slate-800/60 rounded-xl border border-slate-700/50 overflow-hidden">
              <div className="flex items-center gap-3 px-6 py-3 bg-slate-900/50 border-b border-slate-700/50">
                <Terminal className="w-5 h-5 text-green-400" />
                <span className="text-white font-medium">Live Console</span>
                {isRunning && (
                  <div className="ml-auto flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-green-400 text-sm">Running</span>
                  </div>
                )}
              </div>
              <div 
                ref={logConsoleRef}
                className="h-48 sm:h-64 overflow-y-auto p-4 font-mono text-sm bg-slate-950/50"
              >
                {logs.length === 0 ? (
                  <div className="text-slate-500 italic">
                    Select a task preset and click Execute to see live output...
                  </div>
                ) : (
                  logs.map((log, index) => (
                    <div key={index} className="text-green-300 mb-1 animate-fadeIn">
                      <span className="text-slate-500">[{new Date(log.timestamp).toLocaleTimeString()}] </span>
                      {log.event}
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Output */}
            <div className="bg-slate-800/60 rounded-xl border border-slate-700/50 overflow-hidden">
              <div className="flex items-center justify-between px-6 py-3 bg-slate-900/50 border-b border-slate-700/50">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-purple-400" />
                  <span className="text-white font-medium">AI Output</span>
                </div>
                {output && (
                  <button
                    onClick={() => copyToClipboard(output)}
                    className="flex items-center gap-2 px-3 py-1 bg-slate-600/50 hover:bg-slate-600/70 rounded-lg text-slate-300 hover:text-white transition-all duration-200"
                  >
                    <Copy className="w-4 h-4" />
                    <span className="text-sm">Copy</span>
                  </button>
                )}
              </div>
              <div className="h-64 overflow-y-auto p-4 bg-slate-950/50">
                {output ? (
                  <div className="text-slate-300 whitespace-pre-wrap leading-relaxed break-words">
                    {output}
                  </div>
                ) : (
                  <div className="text-slate-500 italic">
                    AI-generated suggestions and analysis will appear here after task completion...
                  </div>
                )}
              </div>
            </div>
            </div>

            {/* Last Task Results */}
            {lastTaskResult && (
              <div className="bg-slate-800/60 rounded-xl border border-slate-700/50 overflow-hidden">
                <div className="flex items-center justify-between px-6 py-3 bg-slate-900/50 border-b border-slate-700/50">
                  <div className="flex items-center gap-3">
                    <Package className="w-5 h-5 text-purple-400" />
                    <span className="text-white font-medium">Last Task Results</span>
                  </div>
                  <button
                    onClick={() => setOutput(lastTaskResult)}
                    className="flex items-center gap-2 px-3 py-1 bg-slate-600/50 hover:bg-slate-600/70 rounded-lg text-slate-300 hover:text-white transition-all duration-200"
                  >
                    <Copy className="w-4 h-4" />
                    <span className="text-sm">Replay</span>
                  </button>
                </div>
                <div className="p-4">
                  <div className="text-slate-400 text-sm line-clamp-3">
                    {lastTaskResult.substring(0, 150)}...
                  </div>
                </div>
              </div>
            )}

            {/* Task Status */}
            {currentTask && (
              <div className="bg-slate-800/60 rounded-xl border border-slate-700/50 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Package className="w-5 h-5 text-orange-400" />
                    <span className="text-white font-medium">Task #{currentTask.id}</span>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                    currentTask.status === 'completed' 
                      ? 'bg-green-600/20 text-green-300 border border-green-500/30'
                      : currentTask.status === 'failed'
                      ? 'bg-red-600/20 text-red-300 border border-red-500/30'
                      : currentTask.status === 'running'
                      ? 'bg-blue-600/20 text-blue-300 border border-blue-500/30'
                      : 'bg-slate-600/20 text-slate-300 border border-slate-500/30'
                  }`}>
                    {currentTask.status === 'completed' && <CheckCircle className="w-4 h-4 inline mr-1" />}
                    {currentTask.status.charAt(0).toUpperCase() + currentTask.status.slice(1)}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
  );
};