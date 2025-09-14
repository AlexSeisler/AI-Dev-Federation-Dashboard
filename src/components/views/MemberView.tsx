import React from 'react';
import { Crown, Lock, Mail, Shield, Zap, User, Key } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { AuthForms } from '../auth/AuthForms';

const premiumFeatures = [
  { name: 'Priority Agent Access', description: 'Skip queues and get instant responses', icon: Zap },
  { name: 'Custom Agent Training', description: 'Train agents on your specific codebase', icon: Crown },
  { name: 'Advanced Analytics', description: 'Detailed insights and performance metrics', icon: Shield },
  { name: 'Private Repositories', description: 'Work with confidential projects securely', icon: Lock }
];

export const MemberView: React.FC = () => {
  const { user } = useAuth();

  // Show auth forms for guests
  if (!user) {
    return <AuthForms />;
  }

  // Show pending state
  if (user.status === 'pending') {
    return (
      <div className="h-full p-8 overflow-auto">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700/50 p-8 backdrop-blur-sm relative overflow-hidden">
            {/* Pending Overlay */}
            <div className="absolute inset-0 bg-slate-900/70 backdrop-blur-sm z-10 flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 border-4 border-orange-500/30 border-t-orange-500 rounded-full animate-spin mx-auto mb-4"></div>
                <h2 className="text-2xl font-bold text-white mb-2">Account Pending Approval</h2>
                <p className="text-slate-300 mb-6 max-w-md">
                  Your account has been created and is awaiting admin approval. You'll receive access once approved.
                </p>
                <div className="text-orange-300 text-sm">
                  Check back soon or contact an administrator
                </div>
              </div>
            </div>

            {/* Content Behind */}
            <div className="blur-sm opacity-50">
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
  }

  // Show approved member content
  return (
    <div className="h-full p-8 overflow-auto">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700/50 p-8 backdrop-blur-sm">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-gradient-to-br from-green-500/20 to-blue-500/20 rounded-xl border border-green-500/30">
              <Crown className="w-8 h-8 text-green-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Welcome, Member!</h1>
              <p className="text-green-300 text-lg">Full Access Unlocked</p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-green-900/20 to-blue-900/20 rounded-xl p-6 border border-green-500/30">
              <h3 className="text-white font-semibold mb-3">🎉 Account Approved!</h3>
              <p className="text-green-300 mb-4">
                Your account has been approved and you now have full access to all member features.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {premiumFeatures.map((feature, index) => (
                <div key={index} className="bg-slate-700/30 rounded-xl p-6 border border-slate-600/30">
                  <feature.icon className="w-8 h-8 text-green-400 mb-3" />
                  <h3 className="font-semibold text-white mb-2">{feature.name}</h3>
                  <p className="text-slate-400 text-sm">{feature.description}</p>
                </div>
              ))}
            </div>

            <div className="bg-gradient-to-r from-green-900/20 to-blue-900/20 rounded-xl p-6 border border-green-500/30">
              <h3 className="text-white font-semibold mb-3">Member Dashboard</h3>
              <div className="bg-slate-900/50 rounded-lg p-8 border border-slate-700/50">
                <div className="text-slate-300 text-center">
                  <Crown className="w-16 h-16 mx-auto mb-4 text-green-400" />
                  <p>Advanced member tools and analytics coming soon!</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };