/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   PLATFORM GRID v3.0.1 ULTIMATE NEXUS                        ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Platform browser grid with filtering                           ║
 * ║  Features: Grid/list view, search, categories, status indicators             ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Grid3X3,
  List,
  ExternalLink,
  CheckCircle,
  AlertCircle,
  Clock,
  Star,
  MoreHorizontal,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface Platform {
  id: string;
  name: string;
  icon: string;
  url: string;
  category: string;
  description?: string;
  status: 'working' | 'partial' | 'broken' | 'unknown';
  features: string[];
  isFavorite?: boolean;
  lastChecked?: Date;
  downloadCount?: number;
}

export interface PlatformGridProps {
  /** Platforms to display */
  platforms: Platform[];
  /** Categories */
  categories?: string[];
  /** On platform click */
  onPlatformClick?: (platform: Platform) => void;
  /** On favorite toggle */
  onFavoriteToggle?: (platform: Platform) => void;
  /** On open external */
  onOpenExternal?: (platform: Platform) => void;
  /** Selected platform */
  selectedPlatform?: Platform | null;
  /** Show favorites only */
  showFavoritesOnly?: boolean;
  /** Additional class names */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// STATUS STYLES
// ═══════════════════════════════════════════════════════════════════════════════

const statusStyles: Record<Platform['status'], { color: string; icon: React.ReactNode; label: string }> = {
  working: {
    color: 'text-green-500',
    icon: <CheckCircle className="w-3.5 h-3.5" />,
    label: 'Working',
  },
  partial: {
    color: 'text-amber-500',
    icon: <Clock className="w-3.5 h-3.5" />,
    label: 'Partial',
  },
  broken: {
    color: 'text-red-500',
    icon: <AlertCircle className="w-3.5 h-3.5" />,
    label: 'Broken',
  },
  unknown: {
    color: 'text-gray-500',
    icon: <MoreHorizontal className="w-3.5 h-3.5" />,
    label: 'Unknown',
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const PlatformGrid: React.FC<PlatformGridProps> = ({
  platforms,
  categories = [],
  onPlatformClick,
  onFavoriteToggle,
  onOpenExternal,
  selectedPlatform,
  showFavoritesOnly = false,
  className,
}) => {
  const [searchQuery, setSearchQuery] = React.useState('');
  const [activeCategory, setActiveCategory] = React.useState('all');
  const [viewMode, setViewMode] = React.useState<'grid' | 'list'>('grid');
  const [showFavorites, setShowFavorites] = React.useState(showFavoritesOnly);

  // Get unique categories
  const allCategories = React.useMemo(() => {
    const cats = new Set(platforms.map((p) => p.category));
    return ['all', ...Array.from(cats), ...categories].filter((v, i, a) => a.indexOf(v) === i);
  }, [platforms, categories]);

  // Filter platforms
  const filteredPlatforms = React.useMemo(() => {
    return platforms.filter((platform) => {
      const matchesSearch =
        !searchQuery ||
        platform.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        platform.description?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = activeCategory === 'all' || platform.category === activeCategory;
      const matchesFavorites = !showFavorites || platform.isFavorite;
      return matchesSearch && matchesCategory && matchesFavorites;
    });
  }, [platforms, searchQuery, activeCategory, showFavorites]);

  // Sort by favorites first, then alphabetically
  const sortedPlatforms = React.useMemo(() => {
    return [...filteredPlatforms].sort((a, b) => {
      if (a.isFavorite && !b.isFavorite) return -1;
      if (!a.isFavorite && b.isFavorite) return 1;
      return a.name.localeCompare(b.name);
    });
  }, [filteredPlatforms]);

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
      <div className="p-4 border-b border-border/50 space-y-3">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search platforms..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-background border border-input text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>

          {/* View toggle & favorites */}
          <div className="flex gap-2">
            <button
              onClick={() => setShowFavorites(!showFavorites)}
              className={cn(
                'p-2 rounded-xl border transition-colors',
                showFavorites
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-500'
                  : 'border-input hover:bg-muted/50'
              )}
              title="Show favorites only"
            >
              <Star className={cn('w-4 h-4', showFavorites && 'fill-current')} />
            </button>
            <div className="flex rounded-xl border border-input overflow-hidden">
              <button
                onClick={() => setViewMode('grid')}
                className={cn(
                  'p-2 transition-colors',
                  viewMode === 'grid' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted/50'
                )}
                title="Grid view"
              >
                <Grid3X3 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={cn(
                  'p-2 transition-colors',
                  viewMode === 'list' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted/50'
                )}
                title="List view"
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Categories */}
        <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
          {allCategories.map((category) => (
            <button
              key={category}
              onClick={() => setActiveCategory(category)}
              className={cn(
                'px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors',
                activeCategory === category
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted/50 hover:bg-muted text-muted-foreground'
              )}
            >
              {category === 'all' ? 'All Platforms' : category}
            </button>
          ))}
        </div>
      </div>

      {/* Grid/List */}
      <div className="p-4 max-h-[500px] overflow-y-auto">
        {sortedPlatforms.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
            <Search className="w-12 h-12 mb-4 opacity-50" />
            <p className="text-sm">No platforms found</p>
            {(searchQuery || showFavorites) && (
              <button
                onClick={() => {
                  setSearchQuery('');
                  setShowFavorites(false);
                }}
                className="mt-2 text-sm text-primary hover:underline"
              >
                Clear filters
              </button>
            )}
          </div>
        ) : viewMode === 'grid' ? (
          <motion.div
            layout
            className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3"
          >
            <AnimatePresence>
              {sortedPlatforms.map((platform, index) => (
                <motion.button
                  key={platform.id}
                  layout
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: index * 0.02 }}
                  onClick={() => onPlatformClick?.(platform)}
                  className={cn(
                    'relative flex flex-col items-center p-4 rounded-xl',
                    'border border-border/50 hover:border-primary/30',
                    'hover:bg-muted/30 transition-all duration-200',
                    'group focus:outline-none focus:ring-2 focus:ring-primary/50',
                    selectedPlatform?.id === platform.id && 'ring-2 ring-primary border-primary/50'
                  )}
                >
                  {/* Favorite indicator */}
                  {platform.isFavorite && (
                    <div className="absolute top-2 left-2">
                      <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
                    </div>
                  )}

                  {/* Status indicator */}
                  <div className={cn('absolute top-2 right-2', statusStyles[platform.status].color)}>
                    {statusStyles[platform.status].icon}
                  </div>

                  {/* Icon */}
                  <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-xl bg-muted/50 flex items-center justify-center mb-2 group-hover:scale-105 transition-transform">
                    {platform.icon.startsWith('http') ? (
                      <img src={platform.icon} alt={platform.name} className="w-8 h-8 rounded-lg" />
                    ) : (
                      <span className="text-2xl">{platform.icon}</span>
                    )}
                  </div>

                  {/* Name */}
                  <span className="text-sm font-medium text-foreground text-center truncate w-full">
                    {platform.name}
                  </span>

                  {/* Category badge */}
                  <span className="text-xs text-muted-foreground mt-0.5 truncate">
                    {platform.category}
                  </span>

                  {/* Quick actions on hover */}
                  <div className="absolute inset-0 flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity bg-background/80 rounded-xl">
                    {onFavoriteToggle && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onFavoriteToggle(platform);
                        }}
                        className="p-2 rounded-lg hover:bg-muted/50 transition-colors"
                        title={platform.isFavorite ? 'Remove from favorites' : 'Add to favorites'}
                      >
                        <Star
                          className={cn(
                            'w-4 h-4',
                            platform.isFavorite ? 'text-amber-500 fill-amber-500' : 'text-muted-foreground'
                          )}
                        />
                      </button>
                    )}
                    {onOpenExternal && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onOpenExternal(platform);
                        }}
                        className="p-2 rounded-lg hover:bg-muted/50 transition-colors"
                        title="Open website"
                      >
                        <ExternalLink className="w-4 h-4 text-muted-foreground" />
                      </button>
                    )}
                  </div>
                </motion.button>
              ))}
            </AnimatePresence>
          </motion.div>
        ) : (
          <ul className="space-y-2">
            <AnimatePresence>
              {sortedPlatforms.map((platform, index) => (
                <motion.li
                  key={platform.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.02 }}
                  onClick={() => onPlatformClick?.(platform)}
                  className={cn(
                    'flex items-center gap-3 p-3 rounded-xl cursor-pointer',
                    'border border-border/50 hover:border-primary/30',
                    'hover:bg-muted/30 transition-all duration-200',
                    selectedPlatform?.id === platform.id && 'ring-2 ring-primary border-primary/50'
                  )}
                >
                  {/* Icon */}
                  <div className="w-10 h-10 rounded-lg bg-muted/50 flex items-center justify-center flex-shrink-0">
                    {platform.icon.startsWith('http') ? (
                      <img src={platform.icon} alt={platform.name} className="w-6 h-6 rounded" />
                    ) : (
                      <span className="text-lg">{platform.icon}</span>
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-foreground truncate">{platform.name}</span>
                      {platform.isFavorite && (
                        <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500 flex-shrink-0" />
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground truncate">
                      {platform.description || platform.category}
                    </p>
                  </div>

                  {/* Status */}
                  <div className={cn('flex items-center gap-1', statusStyles[platform.status].color)}>
                    {statusStyles[platform.status].icon}
                    <span className="text-xs">{statusStyles[platform.status].label}</span>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1">
                    {onFavoriteToggle && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onFavoriteToggle(platform);
                        }}
                        className="p-1.5 rounded-lg hover:bg-muted/50 transition-colors"
                      >
                        <Star
                          className={cn(
                            'w-4 h-4',
                            platform.isFavorite ? 'text-amber-500 fill-amber-500' : 'text-muted-foreground'
                          )}
                        />
                      </button>
                    )}
                    {onOpenExternal && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onOpenExternal(platform);
                        }}
                        className="p-1.5 rounded-lg hover:bg-muted/50 transition-colors"
                      >
                        <ExternalLink className="w-4 h-4 text-muted-foreground" />
                      </button>
                    )}
                  </div>
                </motion.li>
              ))}
            </AnimatePresence>
          </ul>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border/50 bg-muted/30">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>
            {sortedPlatforms.length} platform{sortedPlatforms.length !== 1 ? 's' : ''} available
          </span>
          <span className="flex items-center gap-1">
            <CheckCircle className="w-3 h-3 text-green-500" />
            {platforms.filter((p) => p.status === 'working').length} working
          </span>
        </div>
      </div>
    </div>
  );
};

export default PlatformGrid;
