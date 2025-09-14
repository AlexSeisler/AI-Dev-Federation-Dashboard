import React from 'react';
import { Eye } from 'lucide-react';

export const GuestBanner: React.FC = () => {
  return (
    <div className="h-15 bg-gradient-to-r from-purple-900/20 to-blue-900/20 border-b border-purple-500/20 flex items-center justify-center">
      <div className="flex items-center gap-3 text-purple-300">
        <Eye className="w-5 h-5" />
        <span className="text-sm font-medium tracking-wide">
          Recruiter Mode: Read-only Demo
        </span>
      </div>
    </div>
  );
};