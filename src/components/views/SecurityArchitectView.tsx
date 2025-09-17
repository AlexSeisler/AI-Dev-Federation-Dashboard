import React from 'react';
import { Shield, ExternalLink, Lock, Eye, AlertTriangle } from 'lucide-react';

export const SecurityArchitectView: React.FC = () => {
  return (
    <div className="h-full p-4 sm:p-8 overflow-auto">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700/50 p-6 sm:p-8 backdrop-blur-sm">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-6">
            <div className="p-3 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-xl border border-red-500/30">
              <Shield className="w-6 h-6 sm:w-8 sm:h-8 text-red-400" />
            </div>
            <div className="flex-1">
              <h1 className="text-2xl sm:text-3xl font-bold text-white">Security Architect</h1>
              <p className="text-red-300 text-base sm:text-lg">Security & Compliance Guardian</p>
            </div>
          </div>
          
          <div className="space-y-6 sm:space-y-8">
            <div>
              <p className="text-slate-300 text-base sm:text-lg leading-relaxed">
                The Security Architect ensures your applications are built with security-first principles. 
                From threat modeling to compliance frameworks, it identifies vulnerabilities and implements 
                robust security measures across your entire development lifecycle.
              </p>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-slate-700/30 rounded-xl p-4 sm:p-6 border border-slate-600/30">
                <Lock className="w-5 h-5 sm:w-6 sm:h-6 text-yellow-400 mb-2" />
                <h3 className="font-semibold text-white mb-1 text-sm sm:text-base">Access Control</h3>
                <p className="text-slate-400 text-xs sm:text-sm">Authentication, authorization, and identity management</p>
              </div>
              
              <div className="bg-slate-700/30 rounded-xl p-4 sm:p-6 border border-slate-600/30">
                <Eye className="w-5 h-5 sm:w-6 sm:h-6 text-blue-400 mb-2" />
                <h3 className="font-semibold text-white mb-1 text-sm sm:text-base">Vulnerability Assessment</h3>
                <p className="text-slate-400 text-xs sm:text-sm">Automated security scanning and threat detection</p>
              </div>
              
              <div className="bg-slate-700/30 rounded-xl p-4 sm:p-6 border border-slate-600/30 sm:col-span-2 lg:col-span-1">
                <AlertTriangle className="w-5 h-5 sm:w-6 sm:h-6 text-red-400 mb-2" />
                <h3 className="font-semibold text-white mb-1 text-sm sm:text-base">Compliance</h3>
                <p className="text-slate-400 text-xs sm:text-sm">GDPR, SOC 2, and industry standard compliance</p>
              </div>
            </div>
            
            <div className="bg-gradient-to-r from-slate-700/20 to-slate-800/20 rounded-xl p-6 border border-slate-600/30">
              <h3 className="text-white font-semibold mb-3">Security Reports</h3>
              <div className="bg-slate-900/50 rounded-lg p-8 border border-slate-700/50">
                <div className="text-slate-500 text-center">
                  <Shield className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>Security audit reports and vulnerability assessments</p>
                </div>
              </div>
            </div>
            
            <button className="w-full bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 flex items-center justify-center gap-3 shadow-lg shadow-red-500/20">
              <ExternalLink className="w-5 h-5" />
              Open in GPT
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};