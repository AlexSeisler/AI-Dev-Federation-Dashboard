import React from 'react';
import { Crown, Lock, Mail, Shield, Zap } from 'lucide-react';

const premiumFeatures = [
  { name: 'Priority Agent Access', description: 'Skip queues and get instant responses', icon: Zap },
  { name: 'Custom Agent Training', description: 'Train agents on your specific codebase', icon: Crown },
  { name: 'Advanced Analytics', description: 'Detailed insights and performance metrics', icon: Shield },
  { name: 'Private Repositories', description: 'Work with confidential projects securely', icon: Lock }
];

export const MemberView: React.FC = () => {
  return (
    <div className="h-full p-8 overflow-auto">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700/50 p-8 backdrop-blur-sm relative overflow-hidden">
          {/* Lock Overlay */}
          <div className="absolute inset-0 bg-slate-900/70 backdrop-blur-sm z-10 flex items-center justify-center">
            <div className="text-center">
              <Lock className="w-16 h-16 text-amber-400 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-2">Premium Access Required</h2>
              <p className="text-slate-300 mb-6 max-w-md">
                This section contains exclusive member features. Request access to unlock advanced capabilities.
              </p>
              <button className="bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center gap-2 mx-auto shadow-lg shadow-amber-500/20">
                <Mail className="w-4 h-4" />
                Request Access
              </button>
            </div>
          </div>

          {/* Blurred Content Behind */}
          <div className="blur-sm">
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 bg-gradient-to-br from-amber-500/20 to-orange-500/20 rounded-xl border border-amber-500/30">
                <Crown className="w-8 h-8 text-amber-400" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">Member Portal</h1>
                <p className="text-amber-300 text-lg">Premium Features & Exclusive Access</p>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <p className="text-slate-300 text-lg leading-relaxed">
                  Unlock the full potential of the AI Dev Federation with premium member access. 
                  Get priority support, advanced features, and exclusive tools designed for 
                  professional development teams.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {premiumFeatures.map((feature, index) => (
                  <div key={index} className="bg-slate-700/30 rounded-xl p-6 border border-slate-600/30">
                    <feature.icon className="w-8 h-8 text-amber-400 mb-3" />
                    <h3 className="font-semibold text-white mb-2">{feature.name}</h3>
                    <p className="text-slate-400 text-sm">{feature.description}</p>
                  </div>
                ))}
              </div>

              <div className="bg-gradient-to-r from-amber-900/20 to-orange-900/20 rounded-xl p-6 border border-amber-500/30">
                <h3 className="text-white font-semibold mb-3">Premium Dashboard</h3>
                <div className="bg-slate-900/50 rounded-lg p-8 border border-slate-700/50">
                  <div className="text-slate-500 text-center">
                    <Crown className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Advanced analytics and member tools</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};