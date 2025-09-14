import React from 'react';
import { Eye, Clock, CheckCircle } from 'lucide-react';

interface User {
  id: number;
  email: string;
  role: 'guest' | 'member' | 'admin';
  status: 'pending' | 'approved';
  created_at: string;
}

interface GuestBannerProps {
  user: User | null;
}

export const GuestBanner: React.FC<GuestBannerProps> = ({ user }) => {
  if (!user) {
    // Guest mode
    return (
      <div className="h-15 bg-gradient-to-r from-purple-900/20 to-blue-900/20 border-b border-purple-500/20 flex items-center justify-center">
        <div className="flex items-center gap-3 text-purple-300">
          <Eye className="w-5 h-5" />
          <span className="text-sm font-medium tracking-wide">
            Recruiter Demo Mode (read-only) • Sign up for member access
          </span>
        </div>
      </div>
    );
  }

  if (user.status === 'pending') {
    // Pending approval
    return (
      <div className="h-15 bg-gradient-to-r from-orange-900/20 to-yellow-900/20 border-b border-orange-500/20 flex items-center justify-center">
        <div className="flex items-center gap-3 text-orange-300">
          <Clock className="w-5 h-5 animate-pulse" />
          <span className="text-sm font-medium tracking-wide">
            Account pending admin approval • Check back soon
          </span>
        </div>
      </div>
    );
  }

  if (user.status === 'approved') {
    // Approved member - show minimal banner or hide
    return (
      <div className="h-15 bg-gradient-to-r from-green-900/10 to-blue-900/10 border-b border-green-500/10 flex items-center justify-center">
        <div className="flex items-center gap-3 text-green-300/70">
          <CheckCircle className="w-4 h-4" />
          <span className="text-xs font-medium tracking-wide">
            Welcome back, {user.email}
          </span>
        </div>
      </div>
    );
  }

  // Default fallback
  return (
    <div className="h-15 bg-gradient-to-r from-purple-900/20 to-blue-900/20 border-b border-purple-500/20 flex items-center justify-center">
      <div className="flex items-center gap-3 text-purple-300">
        <Eye className="w-5 h-5" />
        <span className="text-sm font-medium tracking-wide">
          AI Dev Federation Dashboard
        </span>
      </div>
    </div>
  );
};