import React from 'react';
import { Users, ExternalLink, Star, MessageCircle, Sparkles } from 'lucide-react';

const communityStats = [
  { label: 'Members', value: '4', icon: Users },
  { label: 'Live Sessions', value: '7', icon: Star },
  { label: 'Discussions', value: '23', icon: MessageCircle }
];

export const CommunityView: React.FC = () => {
  return (
    <div className="h-full p-4 sm:p-8 overflow-auto bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-5xl mx-auto w-full">
        <div className="rounded-2xl border border-cyan-500/30 bg-gradient-to-br from-slate-900/90 to-slate-950/90 shadow-lg shadow-cyan-500/10 overflow-hidden">
          
          {/* Removed the Banner */}

          {/* Header */}
          <div className="flex flex-col sm:flex-row items-center gap-6 px-6 py-8 border-b border-slate-700/50">
            <img
              src="/assets/AIDevTrifectaLogo.png"
              alt="AI Dev: Trifecta Logo"
              className="w-20 h-20 sm:w-24 sm:h-24 object-contain"
            />
            <div className="text-center sm:text-left">
              <h1 className="text-3xl sm:text-4xl font-bold text-white">AI Dev: Trifecta</h1>
              <p className="text-cyan-300 text-lg mt-1">Where the Federation meets real builders</p>
            </div>
          </div>
          
          <div className="p-6 sm:p-8 space-y-8">
            {/* Community Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {communityStats.map((stat, index) => (
                <div key={index} className="rounded-xl p-6 bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 text-center hover:border-cyan-500/50 transition">
                  <stat.icon className="w-8 h-8 text-cyan-400 mx-auto mb-3" />
                  <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
                  <div className="text-slate-400 text-sm">{stat.label}</div>
                </div>
              ))}
            </div>

            {/* Skool Link */}
            <div className="rounded-xl p-6 border border-cyan-500/30 bg-gradient-to-r from-cyan-700/20 to-blue-800/20">
              <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
                <div>
                  <h3 className="text-white font-semibold text-xl mb-2">Join Our Skool Community</h3>
                  <p className="text-cyan-300 mb-4 max-w-lg">
                    Pilot users are onboarding, testing tools, and shipping faster inside the Trifecta.
                  </p>
                  <button
                    onClick={() =>
                      window.open(
                        'https://www.skool.com/acs-results-4297/about?ref=6827c5683eb14f0892937e9c1c30c835',
                        '_blank'
                      )
                    }
                    className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20"
                  >
                    <ExternalLink className="w-4 h-4" />
                    Join the Community
                  </button>
                </div>
                <div className="self-center">
                  <img
                    src="/assets/AIDevTrifectaLogo.png"
                    alt="AI Dev: Trifecta Logo"
                    className="w-24 h-24 object-contain opacity-90"
                  />
                </div>
              </div>
            </div>

            {/* Proof Angle */}
            <div className="rounded-xl p-6 border border-slate-700/50 bg-gradient-to-r from-slate-800/50 to-slate-900/50">
              <h3 className="text-white font-semibold mb-4">Mission</h3>
              <p className="text-slate-300 leading-relaxed">
                The AI Dev: Trifecta Community is where you unlock 10x execution and outbuild teams. It’s not just about theory - it’s about turning your ideas into real, scalable systems. You’ll build faster, ship sooner, and leave traditional dev teams behind. With the right tools and support, you’ll transform vision into reality, outpacing 99% of devs and building with unmatched speed.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
