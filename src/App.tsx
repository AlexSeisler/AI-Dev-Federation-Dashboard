/**
 * App.tsx — Frontend Entrypoint
 * =============================
 *
 * This is the main React container for the **AI Dev Federation Dashboard**.
 *
 * Responsibilities:
 * - Initialize the layout shell (sidebar, banners, tab switching).
 * - Handle auth state (user, loading state).
 * - Keep backend service alive with a wakeup ping.
 * - Route between all agent views (CIAN, System Architect, Security Architect, DevBot, Community, Member, Admin).
 *
 */

import React, { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';
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

export type AgentTab =
  | 'cian'
  | 'system-architect'
  | 'security-architect'
  | 'devbot'
  | 'community'
  | 'member'
  | 'admin';

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const { user, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<AgentTab>('cian');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // ----------------------------------------------------
  // Wake backend when app loads (to prevent cold starts)
  // ----------------------------------------------------
  useEffect(() => {
    const wakeServer = async () => {
      let retries = 3;
      while (retries > 0) {
        try {
          const res = await fetch(`${API_URL}/health/ping`);
          if (res.ok) {
            console.log("✅ Backend awake");
            return;
          }
        } catch (err) {
          console.warn("⚠️ Wakeup ping failed, retrying...");
        }
        retries--;
        await new Promise((r) => setTimeout(r, 3000));
      }
    };

    wakeServer();
  }, []);

  // ----------------------------------------------------
  // Loading state
  // ----------------------------------------------------
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

  // ----------------------------------------------------
  // Tab Router
  // ----------------------------------------------------
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
        return <MemberView onTabChange={setActiveTab} />;
      case 'admin':
        return <AdminView />;
      default:
        return <CianView />;
    }
  };

  // ----------------------------------------------------
  // Layout
  // ----------------------------------------------------
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <GuestBanner user={user} />
      
      {/* Mobile Header */}
      <div className="lg:hidden bg-slate-800/50 border-b border-slate-700/50 backdrop-blur-sm p-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            AI Dev Federation
          </h1>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 text-slate-300 hover:text-white hover:bg-slate-700/50 rounded-lg transition-all duration-200"
          >
            {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      <div className="flex h-[calc(100vh-60px)] lg:h-[calc(100vh-60px)]">
        {/* Mobile Overlay */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
        
        <Sidebar 
          activeTab={activeTab} 
          onTabChange={(tab) => {
            setActiveTab(tab);
            setSidebarOpen(false);
          }} 
          user={user}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        <main className="flex-1 overflow-hidden w-full lg:w-auto">
          <div className="h-full transition-all duration-300 ease-in-out">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
