import React from 'react';
import { Users, ExternalLink, Star, Calendar, MessageCircle } from 'lucide-react';

const roadmapItems = [
  'Advanced AI agent collaboration',
  'Real-time code review integration',
  'Custom agent training workflows',
  'Enterprise security features',
  'Multi-repository orchestration'
];

const communityStats = [
  { label: 'Active Members', value: '2,847', icon: Users },
  { label: 'Projects', value: '1,293', icon: Star },
  { label: 'Discussions', value: '8,429', icon: MessageCircle }
];

export const CommunityView: React.FC = () => {
  return (
    <div className="h-full p-8 overflow-auto">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700/50 p-8 backdrop-blur-sm">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl border border-purple-500/30">
              <Users className="w-8 h-8 text-purple-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Community Hub</h1>
              <p className="text-purple-300 text-lg">Connect, Learn, Collaborate</p>
            </div>
          </div>
          
          <div className="space-y-8">
            {/* Community Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {communityStats.map((stat, index) => (
                <div key={index} className="bg-slate-700/30 rounded-xl p-6 border border-slate-600/30 text-center">
                  <stat.icon className="w-8 h-8 text-purple-400 mx-auto mb-3" />
                  <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
                  <div className="text-slate-400 text-sm">{stat.label}</div>
                </div>
              ))}
            </div>

            {/* Skool Link */}
            <div className="bg-gradient-to-r from-purple-900/20 to-pink-900/20 rounded-xl p-6 border border-purple-500/30">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white font-semibold text-xl mb-2">Join Our Skool Community</h3>
                  <p className="text-purple-300 mb-4">
                    Access exclusive content, participate in discussions, and collaborate with fellow developers
                  </p>
                  <button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 flex items-center gap-2 shadow-lg shadow-purple-500/20">
                    <ExternalLink className="w-4 h-4" />
                    Join Skool Community
                  </button>
                </div>
                <div className="text-6xl opacity-20">🎓</div>
              </div>
            </div>

            {/* Member Badges */}
            <div className="bg-gradient-to-r from-slate-700/20 to-slate-800/20 rounded-xl p-6 border border-slate-600/30">
              <h3 className="text-white font-semibold mb-4">Community Badges</h3>
              <div className="flex flex-wrap gap-3">
                {['Early Adopter', 'Code Contributor', 'Bug Hunter', 'Documentation Writer', 'Community Helper'].map((badge, index) => (
                  <div
                    key={index}
                    className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-full px-4 py-2 text-blue-300 text-sm font-medium"
                  >
                    ⭐ {badge}
                  </div>
                ))}
              </div>
            </div>

            {/* Roadmap */}
            <div className="bg-gradient-to-r from-slate-700/20 to-slate-800/20 rounded-xl p-6 border border-slate-600/30">
              <div className="flex items-center gap-3 mb-4">
                <Calendar className="w-5 h-5 text-orange-400" />
                <h3 className="text-white font-semibold">Development Roadmap</h3>
              </div>
              <div className="space-y-3">
                {roadmapItems.map((item, index) => (
                  <div key={index} className="flex items-center gap-3 text-slate-300">
                    <div className="w-2 h-2 bg-orange-400 rounded-full flex-shrink-0" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
              <div className="mt-4 text-slate-400 text-sm">
                🚀 More features coming soon! Vote on priorities in our community.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};