import React from 'react';
import { Cpu, ExternalLink, Database, Cloud, GitBranch } from 'lucide-react';

export const SystemArchitectView: React.FC = () => {
  return (
    <div className="h-full p-8 overflow-auto">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700/50 p-8 backdrop-blur-sm">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-gradient-to-br from-green-500/20 to-teal-500/20 rounded-xl border border-green-500/30">
              <Cpu className="w-8 h-8 text-green-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">System Architect</h1>
              <p className="text-green-300 text-lg">Infrastructure Design & Scalability Expert</p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div>
              <p className="text-slate-300 text-lg leading-relaxed">
                The System Architect specializes in designing robust, scalable infrastructure solutions. 
                From microservices architecture to cloud deployment strategies, it ensures your systems 
                are built for performance, reliability, and growth.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-700/30 rounded-xl p-4 border border-slate-600/30">
                <Database className="w-6 h-6 text-blue-400 mb-2" />
                <h3 className="font-semibold text-white mb-1">Database Design</h3>
                <p className="text-slate-400 text-sm">Optimal schema design and query optimization</p>
              </div>
              
              <div className="bg-slate-700/30 rounded-xl p-4 border border-slate-600/30">
                <Cloud className="w-6 h-6 text-purple-400 mb-2" />
                <h3 className="font-semibold text-white mb-1">Cloud Architecture</h3>
                <p className="text-slate-400 text-sm">Scalable cloud-native infrastructure patterns</p>
              </div>
              
              <div className="bg-slate-700/30 rounded-xl p-4 border border-slate-600/30">
                <GitBranch className="w-6 h-6 text-orange-400 mb-2" />
                <h3 className="font-semibold text-white mb-1">Microservices</h3>
                <p className="text-slate-400 text-sm">Distributed system design and service mesh</p>
              </div>
            </div>
            
            <div className="bg-gradient-to-r from-slate-700/20 to-slate-800/20 rounded-xl p-6 border border-slate-600/30">
              <h3 className="text-white font-semibold mb-3">Architecture Diagrams</h3>
              <div className="bg-slate-900/50 rounded-lg p-8 border border-slate-700/50">
                <div className="text-slate-500 text-center">
                  <Database className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>System architecture visualizations and diagrams</p>
                </div>
              </div>
            </div>
            
            <button className="w-full bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 flex items-center justify-center gap-3 shadow-lg shadow-green-500/20">
              <ExternalLink className="w-5 h-5" />
              Open in GPT
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};