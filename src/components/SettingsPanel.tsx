/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   SETTINGS PANEL v3.0.1 ULTIMATE NEXUS                       ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Comprehensive settings management panel                        ║
 * ║  Features: Categories, search, save/reset, export/import, validation         ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings,
  ChevronRight,
  Search,
  Save,
  RotateCcw,
  Download,
  Upload,
  Check,
  AlertCircle,
  Monitor,
  DownloadCloud,
  Shield,
  Bell,
  HardDrive,
  Globe,
  Palette,
  Info,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface SettingOption {
  label: string;
  value: string | number | boolean;
  description?: string;
}

export interface SettingItem {
  id: string;
  label: string;
  description?: string;
  type: 'text' | 'number' | 'select' | 'toggle' | 'slider' | 'color' | 'path';
  value: string | number | boolean;
  options?: SettingOption[];
  min?: number;
  max?: number;
  step?: number;
  placeholder?: string;
  required?: boolean;
  validation?: (value: unknown) => string | null;
  category: string;
}

export interface SettingsCategory {
  id: string;
  label: string;
  icon: React.ReactNode;
  description?: string;
}

export interface SettingsPanelProps {
  /** Settings configuration */
  settings: SettingItem[];
  /** Categories */
  categories: SettingsCategory[];
  /** Current values */
  values: Record<string, string | number | boolean>;
  /** On value change */
  onChange: (id: string, value: string | number | boolean) => void;
  /** On save */
  onSave?: () => void;
  /** On reset */
  onReset?: () => void;
  /** On export */
  onExport?: () => void;
  /** On import */
  onImport?: () => void;
  /** Is saving */
  isSaving?: boolean;
  /** Has unsaved changes */
  hasChanges?: boolean;
  /** Additional class names */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULT CATEGORIES
// ═══════════════════════════════════════════════════════════════════════════════

const defaultCategories: SettingsCategory[] = [
  { id: 'general', label: 'General', icon: <Settings className="w-4 h-4" />, description: 'General application settings' },
  { id: 'downloads', label: 'Downloads', icon: <DownloadCloud className="w-4 h-4" />, description: 'Download preferences' },
  { id: 'network', label: 'Network', icon: <Globe className="w-4 h-4" />, description: 'Network and proxy settings' },
  { id: 'appearance', label: 'Appearance', icon: <Palette className="w-4 h-4" />, description: 'Theme and display' },
  { id: 'storage', label: 'Storage', icon: <HardDrive className="w-4 h-4" />, description: 'Storage locations' },
  { id: 'security', label: 'Security', icon: <Shield className="w-4 h-4" />, description: 'Security options' },
  { id: 'notifications', label: 'Notifications', icon: <Bell className="w-4 h-4" />, description: 'Notification preferences' },
];

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const SettingsPanel: React.FC<SettingsPanelProps> = ({
  settings,
  categories = defaultCategories,
  values,
  onChange,
  onSave,
  onReset,
  onExport,
  onImport,
  isSaving = false,
  hasChanges = false,
  className,
}) => {
  const [activeCategory, setActiveCategory] = React.useState(categories[0]?.id || 'general');
  const [searchQuery, setSearchQuery] = React.useState('');
  const [errors, setErrors] = React.useState<Record<string, string>>({});

  // Filter settings by category and search
  const filteredSettings = React.useMemo(() => {
    return settings.filter((setting) => {
      const matchesCategory = setting.category === activeCategory;
      const matchesSearch =
        !searchQuery ||
        setting.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        setting.description?.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [settings, activeCategory, searchQuery]);

  const handleValueChange = (id: string, value: string | number | boolean) => {
    const setting = settings.find((s) => s.id === id);
    if (setting?.validation) {
      const error = setting.validation(value);
      if (error) {
        setErrors((prev) => ({ ...prev, [id]: error }));
        return;
      }
    }
    setErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors[id];
      return newErrors;
    });
    onChange(id, value);
  };

  const renderSettingInput = (setting: SettingItem) => {
    const value = values[setting.id] ?? setting.value;
    const error = errors[setting.id];

    switch (setting.type) {
      case 'toggle':
        return (
          <button
            onClick={() => handleValueChange(setting.id, !value)}
            className={cn(
              'relative w-12 h-6 rounded-full transition-colors',
              value ? 'bg-primary' : 'bg-muted'
            )}
            role="switch"
            aria-checked={!!value}
            aria-label={setting.label}
          >
            <motion.div
              className="absolute top-1 w-4 h-4 rounded-full bg-white shadow-sm"
              animate={{ left: value ? 28 : 4 }}
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            />
          </button>
        );

      case 'select':
        return (
          <select
            value={String(value)}
            onChange={(e) => handleValueChange(setting.id, e.target.value)}
            className="w-full sm:w-48 px-3 py-2 rounded-lg border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
            aria-label={setting.label}
          >
            {setting.options?.map((opt) => (
              <option key={String(opt.value)} value={String(opt.value)}>
                {opt.label}
              </option>
            ))}
          </select>
        );

      case 'slider':
        return (
          <div className="flex items-center gap-4">
            <input
              type="range"
              min={setting.min ?? 0}
              max={setting.max ?? 100}
              step={setting.step ?? 1}
              value={Number(value)}
              onChange={(e) => handleValueChange(setting.id, Number(e.target.value))}
              className="flex-1 h-2 rounded-full appearance-none bg-muted cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary"
              aria-label={setting.label}
            />
            <span className="w-12 text-sm text-muted-foreground text-right">
              {setting.options?.find((o) => o.value === value)?.label || value}
            </span>
          </div>
        );

      case 'number':
        return (
          <input
            type="number"
            min={setting.min}
            max={setting.max}
            step={setting.step}
            value={Number(value)}
            onChange={(e) => handleValueChange(setting.id, Number(e.target.value))}
            placeholder={setting.placeholder}
            className="w-full sm:w-32 px-3 py-2 rounded-lg border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
            aria-label={setting.label}
          />
        );

      case 'color':
        return (
          <div className="flex items-center gap-2">
            <input
              type="color"
              value={String(value)}
              onChange={(e) => handleValueChange(setting.id, e.target.value)}
              className="w-10 h-10 rounded-lg cursor-pointer border border-input"
              aria-label={setting.label}
            />
            <input
              type="text"
              value={String(value)}
              onChange={(e) => handleValueChange(setting.id, e.target.value)}
              className="w-24 px-2 py-1.5 text-sm rounded-lg border border-input bg-background"
            />
          </div>
        );

      case 'path':
        return (
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={String(value)}
              onChange={(e) => handleValueChange(setting.id, e.target.value)}
              placeholder={setting.placeholder}
              className="flex-1 px-3 py-2 rounded-lg border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              aria-label={setting.label}
            />
            <button
              onClick={() => {
                // File dialog would be handled by parent
              }}
              className="px-3 py-2 rounded-lg border border-input hover:bg-muted/50 transition-colors"
            >
              Browse
            </button>
          </div>
        );

      default:
        return (
          <input
            type="text"
            value={String(value)}
            onChange={(e) => handleValueChange(setting.id, e.target.value)}
            placeholder={setting.placeholder}
            className="w-full px-3 py-2 rounded-lg border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
            aria-label={setting.label}
          />
        );
    }
  };

  return (
    <div
      className={cn(
        'flex flex-col sm:flex-row rounded-2xl overflow-hidden',
        'bg-card/80 backdrop-blur-sm border border-border/50',
        'shadow-xl',
        className
      )}
    >
      {/* Sidebar */}
      <div className="w-full sm:w-64 border-b sm:border-b-0 sm:border-r border-border/50 bg-muted/30">
        {/* Search */}
        <div className="p-3 border-b border-border/50">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search settings..."
              className="w-full pl-9 pr-3 py-2 rounded-lg bg-background border border-input text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
        </div>

        {/* Categories */}
        <nav className="p-2 max-h-[300px] sm:max-h-[500px] overflow-y-auto">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setActiveCategory(category.id)}
              className={cn(
                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors',
                activeCategory === category.id
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
              )}
            >
              {category.icon}
              <div className="flex-1 min-w-0">
                <span className="text-sm font-medium block truncate">{category.label}</span>
              </div>
              <ChevronRight
                className={cn(
                  'w-4 h-4 transition-transform',
                  activeCategory === category.id ? 'rotate-90' : ''
                )}
              />
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border/50">
          <div>
            <h2 className="font-semibold text-foreground">
              {categories.find((c) => c.id === activeCategory)?.label}
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              {categories.find((c) => c.id === activeCategory)?.description}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {onExport && (
              <button
                onClick={onExport}
                className="p-2 rounded-lg hover:bg-muted/50 transition-colors"
                title="Export settings"
              >
                <Download className="w-4 h-4 text-muted-foreground" />
              </button>
            )}
            {onImport && (
              <button
                onClick={onImport}
                className="p-2 rounded-lg hover:bg-muted/50 transition-colors"
                title="Import settings"
              >
                <Upload className="w-4 h-4 text-muted-foreground" />
              </button>
            )}
          </div>
        </div>

        {/* Settings list */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence mode="wait">
            {filteredSettings.length === 0 ? (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center py-12 text-muted-foreground"
              >
                <Info className="w-12 h-12 mb-4 opacity-50" />
                <p className="text-sm">No settings found</p>
              </motion.div>
            ) : (
              <motion.div
                key="settings"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-4"
              >
                {filteredSettings.map((setting, index) => (
                  <motion.div
                    key={setting.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-4 rounded-xl border border-border/50 bg-background/50 hover:bg-background/80 transition-colors"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <label className="text-sm font-medium text-foreground block">
                          {setting.label}
                          {setting.required && <span className="text-red-500 ml-1">*</span>}
                        </label>
                        {setting.description && (
                          <p className="text-xs text-muted-foreground mt-0.5">{setting.description}</p>
                        )}
                        {errors[setting.id] && (
                          <p className="text-xs text-red-500 mt-1 flex items-center gap-1">
                            <AlertCircle className="w-3 h-3" />
                            {errors[setting.id]}
                          </p>
                        )}
                      </div>
                      <div className="sm:w-auto">{renderSettingInput(setting)}</div>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-border/50 bg-muted/30">
          <div className="flex items-center gap-2">
            {hasChanges && (
              <span className="text-xs text-amber-500 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                Unsaved changes
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {onReset && (
              <button
                onClick={onReset}
                disabled={!hasChanges}
                className="flex items-center gap-2 px-4 py-2 rounded-lg border border-input hover:bg-muted/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RotateCcw className="w-4 h-4" />
                Reset
              </button>
            )}
            {onSave && (
              <button
                onClick={onSave}
                disabled={!hasChanges || isSaving || Object.keys(errors).length > 0}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSaving ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  >
                    <RotateCcw className="w-4 h-4" />
                  </motion.div>
                ) : (
                  <Save className="w-4 h-4" />
                )}
                Save
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;
