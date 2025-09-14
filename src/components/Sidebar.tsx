import React from 'react';
import { Brain, Cpu, Shield, Bot, Users, Crown, Lock, Settings, LogOut, LogIn, UserPlus } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { AgentTab } from '../App';

interface User {
  id: number;
  email: string;
  role: 'guest' | 'member' | 'admin';
  status: 'pending' | 'approved';
  created_at: string;
}

interface SidebarProps {
  activeTab: AgentTab;
  onTabChange: (tab: AgentTab) => void;
  user: User | null;
}

const agents = [
  { id: 'cian' as const, name: 'CIAN', icon: Brain, description: 'AI Orchestrator' },
  { id: 'system-architect' as const, name: 'System Architect', icon: Cpu, description: 'Infrastructure Design' },
  { id: 'security-architect' as const, name: 'Security Architect', icon: Shield, description: 'Security & Compliance' },
  { id: 'devbot' as const, name: 'DevBot', icon: Bot, description: 'Development Assistant' },
  { id: 'community' as const, name: 'Community', icon: Users, description: 'Collaboration Hub' },
  { id: 'member' as const, name: 'Member', icon: Crown, description: 'Premium Access', locked: true },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, user }) => {
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    onTabChange('cian');
  };

  return (
    <aside className="w-80 bg-slate-800/50 border-r border-slate-700/50 backdrop-blur-sm">
      <div className="p-6 border-b border-slate-700/50">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          AI Dev Federation
        </h1>
        <p className="text-slate-400 text-sm mt-1">Agent Dashboard</p>
      </div>
      
      <nav className="p-4 space-y-2">
        {agents.filter(agent => {
          // Hide member tab if user is guest or pending
          if (agent.id === 'member' && (!user || user.status === 'pending')) {
            return false;
          }
          return true;
        }).map((agent) => {
          const isActive = activeTab === agent.id;
          const isLocked = agent.locked && (!user || user.status !== 'approved');
          
          return (
            <button
              key={agent.id}
              onClick={() => !isLocked && onTabChange(agent.id)}
              disabled={isLocked}
              className={`
                w-full text-left p-4 rounded-xl transition-all duration-200 group
                ${isActive 
                  ? 'bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 shadow-lg shadow-blue-500/10' 
                  : isLocked
                    ? 'bg-slate-700/30 border border-slate-600/30 opacity-60 cursor-not-allowed'
                    : 'bg-slate-700/30 border border-slate-600/30 hover:bg-slate-700/50 hover:border-slate-500/50'
                }
              `}
            >
              <div className="flex items-center gap-3">
                <div className={`
                  p-2 rounded-lg transition-all duration-200
                  ${isActive
                    ? 'bg-blue-500/20 text-blue-400'
                    : isLocked
                      ? 'bg-slate-600/30 text-slate-500'
                      : 'bg-slate-600/30 text-slate-400 group-hover:bg-slate-600/50 group-hover:text-slate-300'
                  }
                `}>
                  {isLocked ? <Lock className="w-5 h-5" /> : <agent.icon className="w-5 h-5" />}
                </div>
                
                <div className="flex-1">
                  <div className={`
                    font-medium transition-colors duration-200
                    ${isActive 
                      ? 'text-white' 
                      : isLocked 
                        ? 'text-slate-500'
                        : 'text-slate-300 group-hover:text-white'
                    }
                  `}>
                    {agent.name}
                  </div>
                  <div className={`
                    text-xs transition-colors duration-200
                    ${isActive 
                      ? 'text-blue-300' 
                      : isLocked
                        ? 'text-slate-600'
                        : 'text-slate-500 group-hover:text-slate-400'
                    }
                  `}>
                    {agent.description}
                  </div>
                </div>
                
                {isActive && (
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
                )}
              </div>
            </button>
          );
        })}

        {/* Admin Panel */}
        {user?.role === 'admin' && (
          <button
            onClick={() => onTabChange('admin')}
            className={`
              w-full text-left p-4 rounded-xl transition-all duration-200 group
              ${activeTab === 'admin'
                ? 'bg-gradient-to-r from-red-600/20 to-orange-600/20 border border-red-500/30 shadow-lg shadow-red-500/10'
                : 'bg-slate-700/30 border border-slate-600/30 hover:bg-slate-700/50 hover:border-slate-500/50'
              }
            `}
          >
            <div className="flex items-center gap-3">
              <div className={`
                p-2 rounded-lg transition-all duration-200
                ${activeTab === 'admin'
                  ? 'bg-red-500/20 text-red-400'
                  : 'bg-slate-600/30 text-slate-400 group-hover:bg-slate-600/50 group-hover:text-slate-300'
                }
              `}>
                <Settings className="w-5 h-5" />
              </div>
              
              <div className="flex-1">
                <div className={`
                  font-medium transition-colors duration-200
                  ${activeTab === 'admin'
                    ? 'text-white'
                    : 'text-slate-300 group-hover:text-white'
                  }
                `}>
                  Admin Panel
                </div>
                <div className={`
                  text-xs transition-colors duration-200
                  ${activeTab === 'admin'
                    ? 'text-red-300'
                    : 'text-slate-500 group-hover:text-slate-400'
                  }
                `}>
                  User Management
                </div>
              </div>
              
              {activeTab === 'admin' && (
                <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse" />
              )}
            </div>
          </button>
        )}
      </nav>

      {/* Auth Controls */}
      <div className="p-4 border-t border-slate-700/50 mt-auto">
        {user ? (
          <div className="space-y-3">
            <div className="text-xs text-slate-400 px-2">
              Signed in as {user.email}
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-700/50 rounded-lg transition-all duration-200"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm">Sign Out</span>
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <button
              onClick={() => onTabChange('member')}
              className="w-full flex items-center gap-3 px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-700/50 rounded-lg transition-all duration-200"
            >
              <UserPlus className="w-4 h-4" />
              <span className="text-sm">Sign Up / Login</span>
            </button>
          </div>
        )}
      </div>
    </aside>
  );
};