import React from 'react';
import { Brain, ExternalLink, Shield, Network, Zap } from 'lucide-react';

export const CianView: React.FC = () => {
  return (
    <div className="h-full p-4 sm:p-8 overflow-auto">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700/50 p-6 sm:p-8 backdrop-blur-sm">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-6">
            <div className="p-3 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-xl border border-blue-500/30">
              <Brain className="w-6 h-6 sm:w-8 sm:h-8 text-blue-400" />
            </div>
            <div className="flex-1">
              <h1 className="text-2xl sm:text-3xl font-bold text-white">CIAN</h1>
              <p className="text-blue-300 text-base sm:text-lg">
                Central Intelligence Automation Network — your second brain.
              </p>
            </div>
          </div>

          <div className="space-y-6 sm:space-y-8">
            <div>
              <p className="text-slate-300 text-base sm:text-lg leading-relaxed">
                CIAN is the **General Manager** of the Federation. It validates inputs, enforces
                the Critical Validation Loop (CVL), and routes execution across agents. Its role is
                orchestration and continuity — ensuring every action aligns with mission truths.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-slate-700/30 rounded-xl p-4 sm:p-6 border border-slate-600/30">
                <Zap className="w-5 h-5 sm:w-6 sm:h-6 text-yellow-400 mb-2" />
                <h3 className="font-semibold text-white mb-1 text-sm sm:text-base">Input Validation</h3>
                <p className="text-slate-400 text-xs sm:text-sm">
                  Applies the Critical Validation Loop (CVL) to every instruction.
                </p>
              </div>

              <div className="bg-slate-700/30 rounded-xl p-4 sm:p-6 border border-slate-600/30">
                <Network className="w-5 h-5 sm:w-6 sm:h-6 text-green-400 mb-2" />
                <h3 className="font-semibold text-white mb-1 text-sm sm:text-base">Execution Routing</h3>
                <p className="text-slate-400 text-xs sm:text-sm">
                  Delegates tasks to System Architect, Security Architect, or DevBot.
                </p>
              </div>

              <div className="bg-slate-700/30 rounded-xl p-4 sm:p-6 border border-slate-600/30 sm:col-span-2 lg:col-span-1">
                <Shield className="w-5 h-5 sm:w-6 sm:h-6 text-purple-400 mb-2" />
                <h3 className="font-semibold text-white mb-1 text-sm sm:text-base">Strategic Anchoring</h3>
                <p className="text-slate-400 text-xs sm:text-sm">
                  Aligns every action to mission-core truths and federation schemas.
                </p>
              </div>
            </div>

            <button
              onClick={() =>
                window.open(
                  'https://chatgpt.com/g/g-6882d194246c8191a7b8974df4419c8d-cian-v0',
                  '_blank'
                )
              }
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 sm:py-4 px-4 sm:px-6 rounded-xl transition-all duration-200 flex items-center justify-center gap-3 shadow-lg shadow-blue-500/20 min-h-[48px]"
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
