import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { GuestBanner } from './components/GuestBanner';
import { CianView } from './components/views/CianView';
import { SystemArchitectView } from './components/views/SystemArchitectView';
import { SecurityArchitectView } from './components/views/SecurityArchitectView';
import { DevBotView } from './components/views/DevBotView';
import { CommunityView } from './components/views/CommunityView';
import { MemberView } from './components/views/MemberView';

export type AgentTab = 'cian' | 'system-architect' | 'security-architect' | 'devbot' | 'community' | 'member';

function App() {
  const [activeTab, setActiveTab] = useState<AgentTab>('cian');

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
      default:
        return <CianView />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <GuestBanner />
      
      <div className="flex h-[calc(100vh-60px)]">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
        
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