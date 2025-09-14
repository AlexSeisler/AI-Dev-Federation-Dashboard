import React, { useState } from 'react';
import { useAuth } from './contexts/AuthContext';
import { Sidebar } from './components/Sidebar';
import { GuestBanner } from './components/GuestBanner';
import { CianView } from './components/views/CianView';
import { SystemArchitectView } from './components/views/SystemArchitectView';
import { SecurityArchitectView } from './components/views/SecurityArchitectView';
import { DevBotView } from './components/views/DevBotView';
import { CommunityView } from './components/views/CommunityView';
import { MemberView } from './components/views/MemberView';
import { AdminView } from './components/views/AdminView';

export type AgentTab = 'cian' | 'system-architect' | 'security-architect' | 'devbot' | 'community' | 'member' | 'admin';

function App() {
  const { user, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<AgentTab>('cian');

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'cian':
        return <CianView />;
      case 'system-architect':
        return <SystemArchitectView />;
      case 'security-architect':
        return <SecurityArchitectView />;
      case 'devbot':
        return <DevBotView />;
      case 'community':
        return <CommunityView />;
      case 'member':
        return <MemberView />;
      case 'admin':
        return <AdminView />;
      default:
        return <CianView />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <GuestBanner user={user} />
      
      <div className="flex h-[calc(100vh-60px)]">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} user={user} />
        
        <main className="flex-1 overflow-hidden">
          <div className="h-full transition-all duration-300 ease-in-out">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;