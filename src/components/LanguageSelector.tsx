/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   LANGUAGE SELECTOR v3.0.1 ULTIMATE NEXUS                    ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Multi-language selector with flags and search                  ║
 * ║  Features: Search, flags, native names, persistent storage, RTL support      ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Globe, Search, Check, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface Language {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
  rtl?: boolean;
}

export interface LanguageSelectorProps {
  /** Current language code */
  value?: string;
  /** On language change */
  onChange?: (language: Language) => void;
  /** Available languages */
  languages?: Language[];
  /** Show native name */
  showNativeName?: boolean;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Placeholder text */
  placeholder?: string;
  /** Show search */
  showSearch?: boolean;
  /** Additional class names */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULT LANGUAGES
// ═══════════════════════════════════════════════════════════════════════════════

const defaultLanguages: Language[] = [
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', flag: '🇮🇳' },
  { code: 'es', name: 'Spanish', nativeName: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'French', nativeName: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'German', nativeName: 'Deutsch', flag: '🇩🇪' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português', flag: '🇧🇷' },
  { code: 'ru', name: 'Russian', nativeName: 'Русский', flag: '🇷🇺' },
  { code: 'ja', name: 'Japanese', nativeName: '日本語', flag: '🇯🇵' },
  { code: 'ko', name: 'Korean', nativeName: '한국어', flag: '🇰🇷' },
  { code: 'zh', name: 'Chinese', nativeName: '中文', flag: '🇨🇳' },
  { code: 'ar', name: 'Arabic', nativeName: 'العربية', flag: '🇸🇦', rtl: true },
  { code: 'tr', name: 'Turkish', nativeName: 'Türkçe', flag: '🇹🇷' },
  { code: 'it', name: 'Italian', nativeName: 'Italiano', flag: '🇮🇹' },
  { code: 'nl', name: 'Dutch', nativeName: 'Nederlands', flag: '🇳🇱' },
  { code: 'pl', name: 'Polish', nativeName: 'Polski', flag: '🇵🇱' },
  { code: 'vi', name: 'Vietnamese', nativeName: 'Tiếng Việt', flag: '🇻🇳' },
  { code: 'th', name: 'Thai', nativeName: 'ไทย', flag: '🇹🇭' },
  { code: 'id', name: 'Indonesian', nativeName: 'Bahasa Indonesia', flag: '🇮🇩' },
  { code: 'ms', name: 'Malay', nativeName: 'Bahasa Melayu', flag: '🇲🇾' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', flag: '🇧🇩' },
];

// ═══════════════════════════════════════════════════════════════════════════════
// LANGUAGE CONTEXT
// ═══════════════════════════════════════════════════════════════════════════════

interface LanguageContextValue {
  language: Language;
  setLanguage: (language: Language) => void;
  languages: Language[];
}

const LanguageContext = React.createContext<LanguageContextValue | undefined>(undefined);

export const useLanguage = (): LanguageContextValue => {
  const context = React.useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export interface LanguageProviderProps {
  children: React.ReactNode;
  defaultLanguage?: string;
  languages?: Language[];
  storageKey?: string;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({
  children,
  defaultLanguage = 'en',
  languages = defaultLanguages,
  storageKey = 'rs-toolkit-language',
}) => {
  const [language, setLanguageState] = React.useState<Language>(() => {
    const stored = localStorage.getItem(storageKey);
    return languages.find((l) => l.code === stored) || languages.find((l) => l.code === defaultLanguage) || languages[0];
  });

  const setLanguage = (newLanguage: Language) => {
    setLanguageState(newLanguage);
    localStorage.setItem(storageKey, newLanguage.code);
    // Update document direction for RTL languages
    document.documentElement.dir = newLanguage.rtl ? 'rtl' : 'ltr';
    document.documentElement.lang = newLanguage.code;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, languages }}>
      {children}
    </LanguageContext.Provider>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  value,
  onChange,
  languages = defaultLanguages,
  showNativeName = true,
  size = 'md',
  placeholder = 'Select language',
  showSearch = true,
  className,
}) => {
  const context = React.useContext(LanguageContext);
  const currentLanguage = languages.find((l) => l.code === value) ?? context?.language ?? languages[0];

  const [isOpen, setIsOpen] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');
  const dropdownRef = React.useRef<HTMLDivElement>(null);

  // Filter languages
  const filteredLanguages = React.useMemo(() => {
    if (!searchQuery) return languages;
    const query = searchQuery.toLowerCase();
    return languages.filter(
      (lang) =>
        lang.name.toLowerCase().includes(query) ||
        lang.nativeName.toLowerCase().includes(query) ||
        lang.code.toLowerCase().includes(query)
    );
  }, [languages, searchQuery]);

  const handleSelect = (language: Language) => {
    context?.setLanguage(language);
    onChange?.(language);
    setIsOpen(false);
    setSearchQuery('');
  };

  // Close on outside click
  React.useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setSearchQuery('');
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const sizeClasses = {
    sm: 'px-2.5 py-1.5 text-sm',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-2.5 text-base',
  };

  return (
    <div ref={dropdownRef} className={cn('relative', className)}>
      {/* Trigger */}
      <motion.button
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center gap-2 rounded-xl border border-border/50 bg-background/80',
          'hover:bg-muted/50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50',
          sizeClasses[size]
        )}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <span className="text-lg">{currentLanguage?.flag}</span>
        <span className="text-foreground font-medium">
          {showNativeName ? currentLanguage?.nativeName : currentLanguage?.name}
        </span>
        <ChevronDown
          className={cn('w-4 h-4 text-muted-foreground transition-transform', isOpen && 'rotate-180')}
        />
      </motion.button>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute z-50 top-full mt-2 w-64 rounded-xl border border-border bg-popover shadow-xl overflow-hidden"
            role="listbox"
          >
            {/* Search */}
            {showSearch && (
              <div className="p-2 border-b border-border/50">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search language..."
                    className="w-full pl-9 pr-3 py-2 rounded-lg bg-muted/30 border border-input text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                    autoFocus
                  />
                </div>
              </div>
            )}

            {/* Language list */}
            <ul className="max-h-60 overflow-y-auto">
              {filteredLanguages.length === 0 ? (
                <li className="px-4 py-3 text-sm text-muted-foreground text-center">
                  No languages found
                </li>
              ) : (
                filteredLanguages.map((language, index) => (
                  <motion.li
                    key={language.code}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.02 }}
                  >
                    <button
                      onClick={() => handleSelect(language)}
                      className={cn(
                        'w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors',
                        currentLanguage?.code === language.code
                          ? 'bg-primary/10 text-primary'
                          : 'hover:bg-muted/50'
                      )}
                      role="option"
                      aria-selected={currentLanguage?.code === language.code}
                    >
                      <span className="text-xl">{language.flag}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">
                          {language.name}
                        </p>
                        {showNativeName && language.nativeName !== language.name && (
                          <p className="text-xs text-muted-foreground truncate">
                            {language.nativeName}
                          </p>
                        )}
                      </div>
                      {currentLanguage?.code === language.code && (
                        <Check className="w-4 h-4 text-primary" />
                      )}
                    </button>
                  </motion.li>
                ))
              )}
            </ul>

            {/* Footer */}
            <div className="px-4 py-2 border-t border-border/50 bg-muted/30">
              <p className="text-xs text-muted-foreground flex items-center gap-1">
                <Globe className="w-3 h-3" />
                {languages.length} languages available
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default LanguageSelector;
