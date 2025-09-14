import React, { useState, useEffect } from 'react';
import { Settings, Users, CheckCircle, Clock, AlertCircle, RefreshCw } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface PendingUser {
  id: number;
  email: string;
  role: string;
  status: string;
  created_at: string;
}

export const AdminView: React.FC = () => {
  const { user, approveUser } = useAuth();
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Mock data for demo purposes
  const mockPendingUsers: PendingUser[] = [
    {
      id: 1,
      email: 'john.doe@example.com',
      role: 'member',
      status: 'pending',
      created_at: '2024-01-15T10:30:00Z'
    },
    {
      id: 2,
      email: 'jane.smith@company.com',
      role: 'member',
      status: 'pending',
      created_at: '2024-01-14T15:45:00Z'
    },
    {
      id: 3,
      email: 'developer@startup.io',
      role: 'member',
      status: 'pending',
      created_at: '2024-01-13T09:20:00Z'
    }
  ];

  useEffect(() => {
    // Simulate loading pending users
    const loadPendingUsers = async () => {
      setIsLoading(true);
      // In a real app, this would fetch from /server/auth/pending-users or similar
      setTimeout(() => {
        setPendingUsers(mockPendingUsers);
        setIsLoading(false);
      }, 1000);
    };

    loadPendingUsers();
  }, []);

  const handleApprove = async (userId: number, email: string) => {
    try {
      const result = await approveUser(userId);
      
      if (result.success) {
        setPendingUsers(prev => prev.filter(u => u.id !== userId));
        setMessage({
          type: 'success',
          text: `Successfully approved ${email}`
        });
      } else {
        setMessage({
          type: 'error',
          text: result.message
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Failed to approve user'
      });
    }

    // Clear message after 3 seconds
    setTimeout(() => setMessage(null), 3000);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (user?.role !== 'admin') {
    return (
      <div className="h-full p-8 overflow-auto">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700/50 p-8 backdrop-blur-sm">
            <div className="text-center">
              <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-2">Access Denied</h2>
              <p className="text-slate-300">Admin privileges required to access this section.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full p-8 overflow-auto">
      <div className="max-w-6xl mx-auto">
        <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700/50 p-8 backdrop-blur-sm">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-xl border border-red-500/30">
              <Settings className="w-8 h-8 text-red-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Admin Panel</h1>
              <p className="text-red-300 text-lg">User Management & System Control</p>
            </div>
          </div>

          {message && (
            <div className={`mb-6 p-4 rounded-lg border flex items-center gap-3 ${
              message.type === 'success' 
                ? 'bg-green-900/20 border-green-500/30 text-green-300'
                : 'bg-red-900/20 border-red-500/30 text-red-300'
            }`}>
              {message.type === 'success' ? (
                <CheckCircle className="w-5 h-5 flex-shrink-0" />
              ) : (
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
              )}
              <span className="text-sm">{message.text}</span>
            </div>
          )}

          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-slate-700/30 rounded-xl p-6 border border-slate-600/30">
                <Users className="w-8 h-8 text-blue-400 mb-3" />
                <div className="text-2xl font-bold text-white mb-1">{pendingUsers.length}</div>
                <div className="text-slate-400 text-sm">Pending Approvals</div>
              </div>
              
              <div className="bg-slate-700/30 rounded-xl p-6 border border-slate-600/30">
                <CheckCircle className="w-8 h-8 text-green-400 mb-3" />
                <div className="text-2xl font-bold text-white mb-1">47</div>
                <div className="text-slate-400 text-sm">Approved Members</div>
              </div>
              
              <div className="bg-slate-700/30 rounded-xl p-6 border border-slate-600/30">
                <Settings className="w-8 h-8 text-purple-400 mb-3" />
                <div className="text-2xl font-bold text-white mb-1">Active</div>
                <div className="text-slate-400 text-sm">System Status</div>
              </div>
            </div>

            {/* Pending Users Table */}
            <div className="bg-slate-700/20 rounded-xl border border-slate-600/30 overflow-hidden">
              <div className="flex items-center justify-between p-6 border-b border-slate-600/30">
                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-orange-400" />
                  <h3 className="text-white font-semibold">Pending User Approvals</h3>
                </div>
                <button
                  onClick={() => window.location.reload()}
                  className="flex items-center gap-2 px-3 py-1 bg-slate-600/50 hover:bg-slate-600/70 rounded-lg text-slate-300 hover:text-white transition-all duration-200"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span className="text-sm">Refresh</span>
                </button>
              </div>

              {isLoading ? (
                <div className="p-8 text-center">
                  <div className="w-8 h-8 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-slate-400">Loading pending users...</p>
                </div>
              ) : pendingUsers.length === 0 ? (
                <div className="p-8 text-center">
                  <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-4 opacity-50" />
                  <p className="text-slate-400">No pending approvals</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-slate-800/50">
                      <tr>
                        <th className="text-left p-4 text-slate-300 font-medium">Email</th>
                        <th className="text-left p-4 text-slate-300 font-medium">Role</th>
                        <th className="text-left p-4 text-slate-300 font-medium">Requested</th>
                        <th className="text-left p-4 text-slate-300 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pendingUsers.map((pendingUser) => (
                        <tr key={pendingUser.id} className="border-t border-slate-600/30 hover:bg-slate-700/20">
                          <td className="p-4">
                            <div className="text-white font-medium">{pendingUser.email}</div>
                          </td>
                          <td className="p-4">
                            <span className="px-2 py-1 bg-blue-600/20 text-blue-300 rounded-full text-xs font-medium">
                              {pendingUser.role}
                            </span>
                          </td>
                          <td className="p-4">
                            <div className="text-slate-400 text-sm">{formatDate(pendingUser.created_at)}</div>
                          </td>
                          <td className="p-4">
                            <button
                              onClick={() => handleApprove(pendingUser.id, pendingUser.email)}
                              className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-2 shadow-lg shadow-green-500/20"
                            >
                              <CheckCircle className="w-4 h-4" />
                              Approve
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};