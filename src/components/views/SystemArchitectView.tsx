import React from 'react';
import { Cpu, ExternalLink, GitBranch, Shield, ClipboardList } from 'lucide-react';

export const SystemArchitectView: React.FC = () => {
  return (
    <div className="h-full p-4 sm:p-8 overflow-auto">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700/50 p-6 sm:p-8 backdrop-blur-sm">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-6">
            <div className="p-3 bg-gradient-to-br from-green-500/20 to-teal-500/20 rounded-xl border border-green-500/30">
              <Cpu className="w-6 h-6 sm:w-8 sm:h-8 text-green-400" />
            </div>
            <div className="flex-1">
              <h1 className="text-2xl sm:text-3xl font-bold text-white">System Architect</h1>
              <p className="text-green-300 text-base sm:text-lg">
                Engineering Architect - designs blueprints, tasks, and DAGs.
              </p>
            </div>
          </div>

          <div className="space-y-6 sm:space-y-8">
            <div>
              <p className="text-slate-300 text-base sm:text-lg leading-relaxed">
                The <strong>System Architect</strong> is the planner of the Federation. It converts
                validated goals into milestones, DAGs, and atomic tasks. It ensures traceability,
                embeds security flags where needed, and routes execution to DevBot, Security
                Architect, or AI IDE. Its role is <em>planning, never execution</em>.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-slate-700/30 rounded-xl p-4 sm:p-6 border border-slate-600/30">
                <ClipboardList className="w-5 h-5 sm:w-6 sm:h-6 text-blue-400 mb-2" />
                <h3 className="font-semibold text-white mb-1 text-sm sm:text-base">
                  Task Decomposition
                </h3>
                <p className="text-slate-400 text-xs sm:text-sm">
                  Breaks high-level goals into milestones and atomic tasks.
                </p>
              </div>

              <div className="bg-slate-700/30 rounded-xl p-4 sm:p-6 border border-slate-600/30">
                <Shield className="w-5 h-5 sm:w-6 sm:h-6 text-purple-400 mb-2" />
                <h3 className="font-semibold text-white mb-1 text-sm sm:text-base">
                  Security Embedding
                </h3>
                <p className="text-slate-400 text-xs sm:text-sm">
                  Flags security-sensitive milestones for Security Architect review.
                </p>
              </div>

              <div className="bg-slate-700/30 rounded-xl p-4 sm:p-6 border border-slate-600/30 sm:col-span-2 lg:col-span-1">
                <GitBranch className="w-5 h-5 sm:w-6 sm:h-6 text-orange-400 mb-2" />
                <h3 className="font-semibold text-white mb-1 text-sm sm:text-base">
                  Execution Routing
                </h3>
                <p className="text-slate-400 text-xs sm:text-sm">
                  Routes tasks to DevBot, Security Architect, or AI IDE based on scope.
                </p>
              </div>
            </div>

            <div className="bg-gradient-to-r from-slate-700/20 to-slate-800/20 rounded-xl p-4 sm:p-6 border border-slate-600/30">
              <h3 className="text-white font-semibold mb-3 text-base sm:text-lg">
                Preview Screenshot
              </h3>
              <div className="bg-slate-900/50 rounded-lg p-4 sm:p-6 border border-slate-700/50">
                <img
                  src="/assets/SystemArchitect.png"
                  alt="System Architect Preview"
                  className="w-full rounded-lg shadow-lg border border-slate-700/50"
                />
              </div>
            </div>

            <button
              onClick={() =>
                window.open(
                  'https://chatgpt.com/g/g-689e88ed8c4c8191a09d4d04969f6f04-systems-architect-v1',
                  '_blank'
                )
              }
              className="w-full bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white font-semibold py-3 sm:py-4 px-4 sm:px-6 rounded-xl transition-all duration-200 flex items-center justify-center gap-3 shadow-lg shadow-green-500/20 min-h-[48px]"
            >
              <ExternalLink className="w-4 h-4 sm:w-5 sm:h-5" />
              <span className="text-sm sm:text-base">Launch Agent</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
