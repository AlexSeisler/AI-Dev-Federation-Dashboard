import React, { useState, useEffect } from 'react';
import { Bot, ChevronDown, Play, Terminal, FileText, Package } from 'lucide-react';

const taskPresets = [
  'Analyze file structure',
  'Find dead code',
  'Propose logging improvements',
  'Add README badges',
  'Security audit',
  'Performance optimization'
];

const mockLogEntries = [
  '🔍 Scanning repository structure...',
  '📁 Found 23 source files to analyze',
  '⚡ Running static analysis...',
  '🎯 Detected 3 potential improvements',
  '📊 Generating performance report...',
  '✅ Analysis complete - 0 critical issues found'
];

const mockDiff = `@@ -1,7 +1,10 @@
 import React from 'react';
+import { useCallback } from 'react';
 
 const Component = ({ data }) => {
-  const handleClick = () => {
+  const handleClick = useCallback(() => {
     console.log(data);
-  };
+  }, [data]);
+
+  // Added memoization for better performance
 
   return (
     <button onClick={handleClick}>`;

const mockArtifacts = [
  { name: 'performance-report.md', type: 'Report', size: '2.3 KB' },
  { name: 'security-audit.json', type: 'Analysis', size: '1.8 KB' },
  { name: 'code-suggestions.diff', type: 'Diff', size: '892 B' },
  { name: 'package-updates.md', type: 'Guide', size: '1.2 KB' }
];

export const DevBotView: React.FC = () => {
  const [selectedPreset, setSelectedPreset] = useState<string>('');
  const [isRunning, setIsRunning] = useState(false);
  const [logIndex, setLogIndex] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning && logIndex < mockLogEntries.length) {
      interval = setInterval(() => {
        setLogs(prev => [...prev, mockLogEntries[logIndex]]);
        setLogIndex(prev => prev + 1);
      }, 1000);
    } else if (isRunning && logIndex >= mockLogEntries.length) {
      setIsRunning(false);
    }
    
    return () => clearInterval(interval);
  }, [isRunning, logIndex]);

  const handleRun = () => {
    if (!selectedPreset) return;
    setIsRunning(true);
    setLogIndex(0);
    setLogs([]);
  };

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
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Control Panel */}
          <div className="lg:col-span-1 space-y-6">
            {/* Repo Selector */}
            <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700/50">
              <h3 className="text-white font-semibold mb-3">Repository</h3>
              <div className="relative">
                <select 
                  disabled
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-slate-400 cursor-not-allowed"
                >
                  <option>sandbox-demo-repo (Guest Mode)</option>
                </select>
                <div className="absolute top-1/2 right-3 transform -translate-y-1/2 pointer-events-none">
                  <ChevronDown className="w-4 h-4 text-slate-500" />
                </div>
              </div>
            </div>

            {/* Task Presets */}
            <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700/50">
              <h3 className="text-white font-semibold mb-3">Task Presets</h3>
              <div className="space-y-2">
                {taskPresets.map((preset, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedPreset(preset)}
                    className={`w-full text-left px-3 py-2 rounded-lg transition-all duration-200 ${
                      selectedPreset === preset
                        ? 'bg-blue-600/30 border border-blue-500/50 text-blue-300'
                        : 'bg-slate-700/30 border border-slate-600/30 text-slate-300 hover:bg-slate-700/50'
                    }`}
                  >
                    {preset}
                  </button>
                ))}
              </div>
            </div>

            {/* Run Button */}
            <button
              onClick={handleRun}
              disabled={!selectedPreset || isRunning}
              className={`w-full py-4 px-6 rounded-xl font-semibold transition-all duration-200 flex items-center justify-center gap-3 ${
                selectedPreset && !isRunning
                  ? 'bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white shadow-lg shadow-green-500/20'
                  : 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
              }`}
            >
              <Play className={`w-5 h-5 ${isRunning ? 'animate-pulse' : ''}`} />
              {isRunning ? 'Running...' : 'Execute Task'}
            </button>
          </div>

          {/* Content Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Log Stream */}
            <div className="bg-slate-800/60 rounded-xl border border-slate-700/50 overflow-hidden">
              <div className="flex items-center gap-3 px-6 py-3 bg-slate-900/50 border-b border-slate-700/50">
                <Terminal className="w-5 h-5 text-green-400" />
                <span className="text-white font-medium">Live Console</span>
              </div>
              <div className="h-64 overflow-y-auto p-4 font-mono text-sm bg-slate-950/50">
                {logs.length === 0 ? (
                  <div className="text-slate-500 italic">
                    Select a task preset and click Execute to see live output...
                  </div>
                ) : (
                  logs.map((log, index) => (
                    <div key={index} className="text-green-300 mb-1 animate-fadeIn">
                      <span className="text-slate-500">$ </span>
                      {log}
                    </div>
                  ))
                )}
                {isRunning && (
                  <div className="text-blue-400 animate-pulse">
                    <span className="text-slate-500">$ </span>
                    Processing...
                  </div>
                )}
              </div>
            </div>

            {/* Diff Viewer */}
            <div className="bg-slate-800/60 rounded-xl border border-slate-700/50 overflow-hidden">
              <div className="flex items-center gap-3 px-6 py-3 bg-slate-900/50 border-b border-slate-700/50">
                <FileText className="w-5 h-5 text-purple-400" />
                <span className="text-white font-medium">Code Diff Preview</span>
              </div>
              <div className="h-64 overflow-y-auto p-4 font-mono text-sm bg-slate-950/50">
                {logs.length > 0 ? (
                  <pre className="text-slate-300">
                    <span className="text-red-400">--- Original</span>
                    <br />
                    <span className="text-green-400">+++ Improved</span>
                    <br />
                    <span className="text-blue-400">{mockDiff}</span>
                  </pre>
                ) : (
                  <div className="text-slate-500 italic">
                    Code differences will appear here after task execution...
                  </div>
                )}
              </div>
            </div>

            {/* Artifacts List */}
            <div className="bg-slate-800/60 rounded-xl border border-slate-700/50">
              <div className="flex items-center gap-3 px-6 py-3 bg-slate-900/50 border-b border-slate-700/50">
                <Package className="w-5 h-5 text-orange-400" />
                <span className="text-white font-medium">Generated Artifacts</span>
              </div>
              <div className="p-4">
                {logs.length > 3 ? (
                  <div className="space-y-2">
                    {mockArtifacts.map((artifact, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg border border-slate-600/30 hover:bg-slate-700/50 transition-colors cursor-pointer"
                      >
                        <div className="flex items-center gap-3">
                          <FileText className="w-4 h-4 text-blue-400" />
                          <div>
                            <div className="text-white text-sm font-medium">{artifact.name}</div>
                            <div className="text-slate-400 text-xs">{artifact.type}</div>
                          </div>
                        </div>
                        <div className="text-slate-400 text-sm">{artifact.size}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-slate-500 italic text-center py-8">
                    Generated files and reports will appear here...
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};