import React, { useState, useEffect, useRef } from 'react';
import { Bot, ChevronDown, Play, Terminal, FileText, Package, AlertCircle, Copy, CheckCircle, Clock } from 'lucide-react';
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

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

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
  const [pastTasks, setPastTasks] = useState<Task[]>([]);
  const [showColdStartMessage, setShowColdStartMessage] = useState(false);
  
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
      body.context = contextData;   // ✅ send object, not JSON string
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

    // ✅ Allow pending users into demo mode
    if (user?.status === 'pending') {
      console.log('User is pending — running in demo mode.');
      // You could also set a UI banner flag here if you want
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
      
      const response = await fetch(`${API_URL}/tasks/run/${selectedPreset}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
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

      // Start streaming logs
      streamTaskLogs(taskId, token);

    } catch (err) {
      console.error('Task start failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to start task');
      setIsRunning(false);
    }
  };


  const streamTaskLogs = (taskId: number, token: string) => {
    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const eventSource = new EventSource(`${API_URL}/tasks/${taskId}/stream?token=${token}`);


    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const logData = JSON.parse(event.data);
        setLogs(prev => [...prev, logData]);
      } catch (err) {
        console.error('Failed to parse log data:', err);
      }
    };

    eventSource.onerror = (event) => {
      console.error('SSE error:', event);
      eventSource.close();
      
      // Fetch final task result
      fetchTaskResult(taskId, token);
    };

    // Fallback: check task completion after 30 seconds
    setTimeout(() => {
      if (eventSource.readyState === EventSource.OPEN) {
        eventSource.close();
        fetchTaskResult(taskId, token);
      }
    }, 30000);
  };

  const fetchTaskResult = async (taskId: number, token: string) => {
    try {
      const response = await fetch(`${API_URL}/tasks/${taskId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const task = await response.json();
        setCurrentTask(task);
        setLogs(task.logs || []);
        
        // Extract output from logs or context
        const outputLog = task.logs?.find((log: LogEntry) => 
          log.event.includes('HF Response:') || log.event.includes('✅')
        );
        if (outputLog) {
          setOutput(outputLog.event.replace('✅ HF Response: ', ''));
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
      // Could add a toast notification here
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  const selectedPresetConfig = taskPresets.find(p => p.id === selectedPreset);

  return (
    <div className="h-full p-6 overflow-auto bg-slate-900/20">
      <div className="max-w-6xl mx-auto">
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

          {/* Cold Start Message */}
          {showColdStartMessage && (
            <div className="mb-4 p-4 bg-orange-900/20 border border-orange-500/30 rounded-lg flex items-center gap-3">
              <Clock className="w-5 h-5 text-orange-400 animate-pulse" />
              <span className="text-orange-300">⚡ Backend waking up (cold start). Please retry in a few seconds.</span>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-4 bg-red-900/20 border border-red-500/30 rounded-lg flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400" />
              <span className="text-red-300">{error}</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Control Panel */}
          <div className="lg:col-span-1 space-y-6">
            {/* Task Presets */}
            <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700/50">
              <h3 className="text-white font-semibold mb-3">Task Presets</h3>
              <div className="space-y-2">
                {taskPresets.map((preset) => (
                  <button
                    key={preset.id}
                    onClick={() => setSelectedPreset(preset.id)}
                    disabled={isRunning}
                    className={`w-full text-left px-3 py-3 rounded-lg transition-all duration-200 ${
                      selectedPreset === preset.id
                        ? 'bg-blue-600/30 border border-blue-500/50 text-blue-300'
                        : 'bg-slate-700/30 border border-slate-600/30 text-slate-300 hover:bg-slate-700/50'
                    } ${isRunning ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <div className="font-medium">{preset.name}</div>
                    <div className="text-xs text-slate-400 mt-1">{preset.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Adaptive Input Fields */}
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
                        placeholder="What would you like to brainstorm about?"
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
                        placeholder="owner/repository"
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
                        placeholder="src/components/App.tsx"
                      />
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Run Button */}
            <button
              onClick={startTask}
              disabled={!selectedPreset || isRunning || !user}
              className={`w-full py-4 px-6 rounded-xl font-semibold transition-all duration-200 flex items-center justify-center gap-3 ${
                !selectedPreset || isRunning || !user
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

          {/* Content Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Log Stream */}
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
                className="h-64 overflow-y-auto p-4 font-mono text-sm bg-slate-950/50"
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

            {/* Output Viewer */}
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
                  <div className="text-slate-300 whitespace-pre-wrap leading-relaxed">
                    {output}
                  </div>
                ) : (
                  <div className="text-slate-500 italic">
                    AI-generated suggestions and analysis will appear here after task completion...
                  </div>
                )}
              </div>
            </div>

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
    </div>
  );
};