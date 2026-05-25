/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   SEARCH BAR v3.0.1 ULTIMATE NEXUS                           ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Advanced search bar with suggestions and history               ║
 * ║  Features: Auto-suggestions, search history, URL validation, keyboard nav    ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  X,
  Clock,
  ArrowRight,
  Link,
  FileVideo,
  FileAudio,
  Image,
  Loader2,
  Globe,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface SearchSuggestion {
  id: string;
  title: string;
  type: 'url' | 'history' | 'suggestion';
  url?: string;
  icon?: React.ReactNode;
  metadata?: string;
}

export interface SearchBarProps {
  /** Current search value */
  value: string;
  /** On value change */
  onChange: (value: string) => void;
  /** On search submit */
  onSubmit: (value: string) => void;
  /** On clear */
  onClear?: () => void;
  /** Placeholder text */
  placeholder?: string;
  /** Search suggestions */
  suggestions?: SearchSuggestion[];
  /** Search history */
  history?: string[];
  /** Is loading */
  isLoading?: boolean;
  /** Show history */
  showHistory?: boolean;
  /** Max history items */
  maxHistoryItems?: number;
  /** Auto focus */
  autoFocus?: boolean;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** On suggestion click */
  onSuggestionClick?: (suggestion: SearchSuggestion) => void;
  /** On history clear */
  onHistoryClear?: () => void;
  /** Additional class names */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

const isValidUrl = (str: string): boolean => {
  try {
    const url = new URL(str);
    return ['http:', 'https:'].includes(url.protocol);
  } catch {
    return false;
  }
};

const getDomainFromUrl = (url: string): string => {
  try {
    return new URL(url).hostname.replace('www.', '');
  } catch {
    return url;
  }
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  onSubmit,
  onClear,
  placeholder = 'Paste a URL or search...',
  suggestions = [],
  history = [],
  isLoading = false,
  showHistory = true,
  maxHistoryItems = 5,
  autoFocus = false,
  size = 'md',
  onSuggestionClick,
  onHistoryClear,
  className,
}) => {
  const [isFocused, setIsFocused] = React.useState(false);
  const [selectedIndex, setSelectedIndex] = React.useState(-1);
  const inputRef = React.useRef<HTMLInputElement>(null);
  const containerRef = React.useRef<HTMLDivElement>(null);

  const isUrl = isValidUrl(value);

  // Combine history and suggestions
  const allSuggestions = React.useMemo(() => {
    const items: SearchSuggestion[] = [];

    // Add URL suggestion if input looks like a URL
    if (value && isUrl) {
      items.push({
        id: 'current-url',
        title: value,
        type: 'url',
        url: value,
        icon: <Link className="w-4 h-4" />,
        metadata: getDomainFromUrl(value),
      });
    }

    // Add history items
    if (showHistory && !value && history.length > 0) {
      history.slice(0, maxHistoryItems).forEach((item, index) => ({
        id: `history-${index}`,
        title: item,
        type: 'history' as const,
        icon: <Clock className="w-4 h-4" />,
      }));
    }

    // Add passed suggestions
    items.push(...suggestions);

    return items;
  }, [value, isUrl, showHistory, history, maxHistoryItems, suggestions]);

  const showDropdown = isFocused && allSuggestions.length > 0;

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.min(prev + 1, allSuggestions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 1, -1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedIndex >= 0 && allSuggestions[selectedIndex]) {
        handleSuggestionClick(allSuggestions[selectedIndex]);
      } else {
        handleSubmit();
      }
    } else if (e.key === 'Escape') {
      setIsFocused(false);
      inputRef.current?.blur();
    }
  };

  const handleSubmit = () => {
    if (value.trim()) {
      onSubmit(value.trim());
      setIsFocused(false);
    }
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    onChange(suggestion.title);
    onSuggestionClick?.(suggestion);
    onSubmit(suggestion.title);
    setIsFocused(false);
  };

  const handleClear = () => {
    onChange('');
    onClear?.();
    inputRef.current?.focus();
  };

  // Close dropdown on outside click
  React.useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsFocused(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const sizeClasses = {
    sm: 'py-2 px-3 text-sm',
    md: 'py-3 px-4 text-base',
    lg: 'py-4 px-5 text-lg',
  };

  return (
    <div ref={containerRef} className={cn('relative w-full', className)}>
      {/* Input container */}
      <div
        className={cn(
          'relative flex items-center rounded-2xl',
          'border-2 transition-all duration-200',
          'bg-background/80 backdrop-blur-sm',
          isFocused ? 'border-primary shadow-lg shadow-primary/10' : 'border-border/50 hover:border-border',
          isLoading && 'pr-20'
        )}
      >
        {/* Search icon */}
        <div className="absolute left-4 flex items-center justify-center">
          {isLoading ? (
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
              <Loader2 className="w-5 h-5 text-primary" />
            </motion.div>
          ) : (
            <Search className={cn('w-5 h-5', isFocused ? 'text-primary' : 'text-muted-foreground')} />
          )}
        </div>

        {/* Input */}
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          autoFocus={autoFocus}
          className={cn(
            'w-full bg-transparent focus:outline-none',
            'placeholder:text-muted-foreground/60',
            sizeClasses[size],
            'pl-12',
            (value || isLoading) && 'pr-20'
          )}
          aria-label="Search"
          aria-autocomplete="list"
          aria-controls="search-suggestions"
          aria-expanded={showDropdown}
        />

        {/* URL badge */}
        {isUrl && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute right-14 flex items-center gap-1 px-2 py-1 rounded-lg bg-primary/10 text-primary text-xs"
          >
            <Globe className="w-3 h-3" />
            <span>URL</span>
          </motion.div>
        )}

        {/* Clear button */}
        {(value || isLoading) && (
          <button
            onClick={handleClear}
            className="absolute right-3 p-1.5 rounded-lg hover:bg-muted/50 transition-colors"
            aria-label="Clear search"
          >
            <X className="w-4 h-4 text-muted-foreground" />
          </button>
        )}
      </div>

      {/* Dropdown */}
      <AnimatePresence>
        {showDropdown && (
          <motion.div
            id="search-suggestions"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.15 }}
            className="absolute z-50 w-full mt-2 rounded-xl border border-border bg-popover shadow-xl overflow-hidden"
            role="listbox"
          >
            {showHistory && !value && history.length > 0 && (
              <div className="flex items-center justify-between px-3 py-2 border-b border-border/50 bg-muted/30">
                <span className="text-xs font-medium text-muted-foreground">Recent searches</span>
                {onHistoryClear && (
                  <button
                    onClick={onHistoryClear}
                    className="text-xs text-primary hover:underline"
                  >
                    Clear
                  </button>
                )}
              </div>
            )}

            <ul className="max-h-80 overflow-y-auto">
              {allSuggestions.map((suggestion, index) => (
                <motion.li
                  key={suggestion.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.02 }}
                >
                  <button
                    onClick={() => handleSuggestionClick(suggestion)}
                    onMouseEnter={() => setSelectedIndex(index)}
                    className={cn(
                      'w-full flex items-center gap-3 px-4 py-3 text-left transition-colors',
                      selectedIndex === index ? 'bg-primary/10' : 'hover:bg-muted/50'
                    )}
                    role="option"
                    aria-selected={selectedIndex === index}
                  >
                    <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-muted/50 flex items-center justify-center">
                      {suggestion.icon || <Sparkles className="w-4 h-4 text-muted-foreground" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">
                        {suggestion.title}
                      </p>
                      {suggestion.metadata && (
                        <p className="text-xs text-muted-foreground truncate">
                          {suggestion.metadata}
                        </p>
                      )}
                    </div>
                    <ArrowRight className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                  </button>
                </motion.li>
              ))}
            </ul>

            {/* Quick tip */}
            {!value && (
              <div className="px-4 py-2 border-t border-border/50 bg-muted/30">
                <p className="text-xs text-muted-foreground">
                  <kbd className="px-1.5 py-0.5 rounded bg-muted font-mono text-[10px]">Enter</kbd>
                  to search •
                  <kbd className="px-1.5 py-0.5 rounded bg-muted font-mono text-[10px]">Esc</kbd>
                  to close
                </p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SearchBar;
