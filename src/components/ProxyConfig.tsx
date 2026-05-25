/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   PROXY CONFIG v3.0.1 ULTIMATE NEXUS                         ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Proxy configuration with multiple protocols                    ║
 * ║  Features: HTTP/SOCKS5 support, test connection, preset management           ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield,
  Globe,
  Lock,
  Unlock,
  Plus,
  Trash2,
  Edit2,
  Check,
  X,
  Loader2,
  AlertCircle,
  Wifi,
  WifiOff,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface ProxyConfig {
  id: string;
  name: string;
  protocol: 'http' | 'https' | 'socks4' | 'socks5';
  host: string;
  port: number;
  username?: string;
  password?: string;
  isActive?: boolean;
  isDefault?: boolean;
}

export interface ProxyConfigProps {
  /** Current proxy configurations */
  proxies?: ProxyConfig[];
  /** Active proxy ID */
  activeProxyId?: string;
  /** On proxy add */
  onAdd?: (proxy: Omit<ProxyConfig, 'id'>) => void;
  /** On proxy update */
  onUpdate?: (proxy: ProxyConfig) => void;
  /** On proxy delete */
  onDelete?: (id: string) => void;
  /** On proxy activate */
  onActivate?: (id: string) => void;
  /** On test connection */
  onTest?: (proxy: ProxyConfig) => Promise<boolean>;
  /** Show test button */
  showTest?: boolean;
  /** Additional class names */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const ProxyConfig: React.FC<ProxyConfigProps> = ({
  proxies = [],
  activeProxyId,
  onAdd,
  onUpdate,
  onDelete,
  onActivate,
  onTest,
  showTest = true,
  className,
}) => {
  const [isAdding, setIsAdding] = React.useState(false);
  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [testingId, setTestingId] = React.useState<string | null>(null);
  const [testResults, setTestResults] = React.useState<Record<string, boolean>>({});

  const [formData, setFormData] = React.useState<Omit<ProxyConfig, 'id'>>({
    name: '',
    protocol: 'http',
    host: '',
    port: 8080,
    username: '',
    password: '',
  });

  const resetForm = () => {
    setFormData({
      name: '',
      protocol: 'http',
      host: '',
      port: 8080,
      username: '',
      password: '',
    });
    setIsAdding(false);
    setEditingId(null);
  };

  const handleSubmit = () => {
    if (!formData.host || !formData.port) return;

    if (editingId) {
      onUpdate?.({ ...formData, id: editingId });
    } else {
      onAdd?.(formData);
    }
    resetForm();
  };

  const handleEdit = (proxy: ProxyConfig) => {
    const { id, ...data } = proxy;
    setFormData(data);
    setEditingId(id);
    setIsAdding(true);
  };

  const handleTest = async (proxy: ProxyConfig) => {
    setTestingId(proxy.id);
    try {
      const result = await onTest?.(proxy);
      setTestResults((prev) => ({ ...prev, [proxy.id]: result ?? false }));
    } catch {
      setTestResults((prev) => ({ ...prev, [proxy.id]: false }));
    }
    setTestingId(null);
  };

  const activeProxy = proxies.find((p) => p.id === activeProxyId);

  return (
    <div
      className={cn(
        'rounded-2xl overflow-hidden',
        'bg-card/80 backdrop-blur-sm border border-border/50',
        'shadow-xl',
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-border/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={cn(
                'w-10 h-10 rounded-xl flex items-center justify-center',
                activeProxy ? 'bg-green-500/20' : 'bg-muted/50'
              )}
            >
              {activeProxy ? (
                <Shield className="w-5 h-5 text-green-500" />
              ) : (
                <Globe className="w-5 h-5 text-muted-foreground" />
              )}
            </div>
            <div>
              <h3 className="font-semibold text-foreground">Proxy Settings</h3>
              <p className="text-xs text-muted-foreground">
                {activeProxy ? `Using ${activeProxy.name}` : 'No proxy configured'}
              </p>
            </div>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setIsAdding(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium"
          >
            <Plus className="w-4 h-4" />
            Add Proxy
          </motion.button>
        </div>
      </div>

      {/* Proxy list */}
      <div className="max-h-[400px] overflow-y-auto">
        {proxies.length === 0 && !isAdding ? (
          <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
            <WifiOff className="w-12 h-12 mb-4 opacity-50" />
            <p className="text-sm">No proxy configured</p>
            <p className="text-xs mt-1">Add a proxy to route your downloads</p>
          </div>
        ) : (
          <ul className="divide-y divide-border/50">
            <AnimatePresence>
              {proxies.map((proxy) => (
                <motion.li
                  key={proxy.id}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className={cn(
                    'p-4 transition-colors',
                    activeProxyId === proxy.id && 'bg-primary/5'
                  )}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      {/* Status indicator */}
                      <div
                        className={cn(
                          'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
                          activeProxyId === proxy.id ? 'bg-green-500/20' : 'bg-muted/50'
                        )}
                      >
                        {activeProxyId === proxy.id ? (
                          <Lock className="w-4 h-4 text-green-500" />
                        ) : (
                          <Unlock className="w-4 h-4 text-muted-foreground" />
                        )}
                      </div>

                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-foreground">{proxy.name}</span>
                          <span className="px-1.5 py-0.5 rounded text-xs bg-muted/50 text-muted-foreground uppercase">
                            {proxy.protocol}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground mt-0.5">
                          {proxy.host}:{proxy.port}
                        </p>
                        {proxy.username && (
                          <p className="text-xs text-muted-foreground mt-0.5">
                            Auth: {proxy.username}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-1">
                      {/* Test result indicator */}
                      {testResults[proxy.id] !== undefined && (
                        <div
                          className={cn(
                            'p-1.5 rounded',
                            testResults[proxy.id] ? 'text-green-500' : 'text-red-500'
                          )}
                        >
                          {testResults[proxy.id] ? (
                            <Check className="w-4 h-4" />
                          ) : (
                            <AlertCircle className="w-4 h-4" />
                          )}
                        </div>
                      )}

                      {/* Test button */}
                      {showTest && (
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => handleTest(proxy)}
                          disabled={testingId === proxy.id}
                          className="p-1.5 rounded-lg hover:bg-muted/50 transition-colors"
                          title="Test connection"
                        >
                          {testingId === proxy.id ? (
                            <Loader2 className="w-4 h-4 animate-spin text-primary" />
                          ) : (
                            <Wifi className="w-4 h-4 text-muted-foreground" />
                          )}
                        </motion.button>
                      )}

                      {/* Activate button */}
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => onActivate?.(proxy.id)}
                        className={cn(
                          'p-1.5 rounded-lg transition-colors',
                          activeProxyId === proxy.id
                            ? 'bg-green-500/20 text-green-500'
                            : 'hover:bg-muted/50 text-muted-foreground'
                        )}
                        title={activeProxyId === proxy.id ? 'Active' : 'Activate'}
                      >
                        {activeProxyId === proxy.id ? (
                          <Check className="w-4 h-4" />
                        ) : (
                          <Unlock className="w-4 h-4" />
                        )}
                      </motion.button>

                      {/* Edit button */}
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleEdit(proxy)}
                        className="p-1.5 rounded-lg hover:bg-muted/50 transition-colors"
                        title="Edit"
                      >
                        <Edit2 className="w-4 h-4 text-muted-foreground" />
                      </motion.button>

                      {/* Delete button */}
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => onDelete?.(proxy.id)}
                        className="p-1.5 rounded-lg hover:bg-red-500/10 text-red-500 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </motion.button>
                    </div>
                  </div>
                </motion.li>
              ))}
            </AnimatePresence>
          </ul>
        )}
      </div>

      {/* Add/Edit form */}
      <AnimatePresence>
        {isAdding && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-t border-border/50 overflow-hidden"
          >
            <div className="p-4 space-y-4">
              <h4 className="font-medium text-foreground">
                {editingId ? 'Edit Proxy' : 'Add New Proxy'}
              </h4>

              <div className="grid grid-cols-2 gap-3">
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-xs text-muted-foreground mb-1">Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="My Proxy"
                    className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>

                <div>
                  <label className="block text-xs text-muted-foreground mb-1">Protocol</label>
                  <select
                    value={formData.protocol}
                    onChange={(e) => setFormData({ ...formData, protocol: e.target.value as ProxyConfig['protocol'] })}
                    className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  >
                    <option value="http">HTTP</option>
                    <option value="https">HTTPS</option>
                    <option value="socks4">SOCKS4</option>
                    <option value="socks5">SOCKS5</option>
                  </select>
                </div>

                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-xs text-muted-foreground mb-1">Host</label>
                  <input
                    type="text"
                    value={formData.host}
                    onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                    placeholder="proxy.example.com"
                    className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>

                <div>
                  <label className="block text-xs text-muted-foreground mb-1">Port</label>
                  <input
                    type="number"
                    value={formData.port}
                    onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) || 0 })}
                    placeholder="8080"
                    className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>

                <div className="col-span-2">
                  <label className="block text-xs text-muted-foreground mb-1">
                    Username (optional)
                  </label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    placeholder="username"
                    className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>

                <div className="col-span-2">
                  <label className="block text-xs text-muted-foreground mb-1">
                    Password (optional)
                  </label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    placeholder="••••••••"
                    className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2">
                <button
                  onClick={resetForm}
                  className="px-4 py-2 rounded-lg border border-input hover:bg-muted/50 text-sm transition-colors"
                >
                  Cancel
                </button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleSubmit}
                  disabled={!formData.host || !formData.port}
                  className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium disabled:opacity-50"
                >
                  {editingId ? 'Update' : 'Add'} Proxy
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-border/50 bg-muted/30">
        <p className="text-xs text-muted-foreground flex items-center gap-1">
          <Shield className="w-3 h-3" />
          {proxies.length} proxy{proxies.length !== 1 ? 's' : ''} configured
          {activeProxy && ` • ${activeProxy.name} active`}
        </p>
      </div>
    </div>
  );
};

export default ProxyConfig;
