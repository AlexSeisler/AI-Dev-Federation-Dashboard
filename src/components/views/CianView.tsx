import React from 'react';
import { Brain, ExternalLink, Zap, Network, Cpu } from 'lucide-react';

export const CianView: React.FC = () => {
  return (
    <div className="h-full p-8 overflow-auto">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700/50 p-8 backdrop-blur-sm">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-xl border border-blue-500/30">
              <Brain className="w-8 h-8 text-blue-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">CIAN</h1>
              <p className="text-blue-300 text-lg">Collective Intelligence & Automation Network</p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div>
              <p className="text-slate-300 text-lg leading-relaxed">
                CIAN serves as the central orchestrator of the AI Dev Federation, coordinating between specialized agents 
                to deliver comprehensive development solutions. Acting as the primary interface for complex multi-agent workflows.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-700/30 rounded-xl p-4 border border-slate-600/30">
                <Zap className="w-6 h-6 text-yellow-400 mb-2" />
                <h3 className="font-semibold text-white mb-1">Intelligent Routing</h3>
                <p className="text-slate-400 text-sm">Automatically delegates tasks to appropriate specialist agents</p>
              </div>
              
              <div className="bg-slate-700/30 rounded-xl p-4 border border-slate-600/30">
                <Network className="w-6 h-6 text-green-400 mb-2" />
                <h3 className="font-semibold text-white mb-1">Workflow Orchestration</h3>
                <p className="text-slate-400 text-sm">Manages complex multi-step development processes</p>
              </div>
              
              <div className="bg-slate-700/30 rounded-xl p-4 border border-slate-600/30">
                <Cpu className="w-6 h-6 text-purple-400 mb-2" />
                <h3 className="font-semibold text-white mb-1">Context Synthesis</h3>
                <p className="text-slate-400 text-sm">Combines insights from all agents into coherent solutions</p>
              </div>
            </div>
            
            <div className="bg-gradient-to-r from-slate-700/20 to-slate-800/20 rounded-xl p-6 border border-slate-600/30">
              <h3 className="text-white font-semibold mb-3">Preview Screenshots</h3>
              <div className="bg-slate-900/50 rounded-lg p-8 border border-slate-700/50">
                <div className="text-slate-500 text-center">
                  <Cpu className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>Interactive CIAN interface screenshots will appear here</p>
                </div>
              </div>
            </div>
            
            <button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 flex items-center justify-center gap-3 shadow-lg shadow-blue-500/20">
              <ExternalLink className="w-5 h-5" />
              Open in GPT
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};