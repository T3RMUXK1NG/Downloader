/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    USE MEDIA QUERY HOOK v3.0.1 ULTIMATE NEXUS                 ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Responsive design media query hook                            ║
 * ║  Features: Breakpoints, SSR safe, callbacks, debouncing                     ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module hooks/useMediaQuery
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

'use client';

import { useCallback, useEffect, useState } from 'react';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export type Breakpoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';

export interface BreakpointConfig {
  xs: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  '2xl': number;
}

export interface UseMediaQueryOptions {
  /** Custom breakpoints */
  breakpoints?: BreakpointConfig;
  /** SSR default value */
  defaultMatches?: boolean;
  /** Debounce delay in ms */
  debounceDelay?: number;
}

export interface UseMediaQueryReturn {
  /** Current breakpoint */
  breakpoint: Breakpoint;
  /** Is mobile (< md) */
  isMobile: boolean;
  /** Is tablet (md - lg) */
  isTablet: boolean;
  /** Is desktop (> lg) */
  isDesktop: boolean;
  /** Check if matches query */
  matches: (query: string) => boolean;
  /** Is specific breakpoint */
  isBreakpoint: (bp: Breakpoint) => boolean;
  /** Is above breakpoint */
  isAbove: (bp: Breakpoint) => boolean;
  /** Is below breakpoint */
  isBelow: (bp: Breakpoint) => boolean;
  /** Screen width */
  screenWidth: number;
  /** Screen height */
  screenHeight: number;
  /** Orientation */
  orientation: 'portrait' | 'landscape';
  /** Is touch device */
  isTouchDevice: boolean;
  /** Device pixel ratio */
  pixelRatio: number;
  /** Prefers reduced motion */
  prefersReducedMotion: boolean;
  /** Prefers dark mode */
  prefersDarkMode: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════════════════

export const DEFAULT_BREAKPOINTS: BreakpointConfig = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
};

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * useMediaQuery Hook
 * @description Responsive design media query with breakpoints and device detection
 * @param options Hook options
 * @returns Media query controls and state
 */
export function useMediaQuery(options: UseMediaQueryOptions = {}): UseMediaQueryReturn {
  const {
    breakpoints = DEFAULT_BREAKPOINTS,
    defaultMatches = false,
    debounceDelay = 100,
  } = options;

  // State
  const [breakpoint, setBreakpoint] = useState<Breakpoint>('xs');
  const [screenWidth, setScreenWidth] = useState(0);
  const [screenHeight, setScreenHeight] = useState(0);
  const [orientation, setOrientation] = useState<'portrait' | 'landscape'>('portrait');
  const [isTouchDevice, setIsTouchDevice] = useState(false);
  const [pixelRatio, setPixelRatio] = useState(1);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const [prefersDarkMode, setPrefersDarkMode] = useState(false);

  // ═══════════════════════════════════════════════════════════════════════════
  // MEDIA QUERY MATCHER
  // ═══════════════════════════════════════════════════════════════════════════

  const useMatchMedia = (query: string): boolean => {
    const [matches, setMatches] = useState(defaultMatches);

    useEffect(() => {
      if (typeof window === 'undefined') return;

      const mediaQuery = window.matchMedia(query);
      setMatches(mediaQuery.matches);

      const handler = (event: MediaQueryListEvent) => {
        setMatches(event.matches);
      };

      mediaQuery.addEventListener('change', handler);
      return () => mediaQuery.removeEventListener('change', handler);
    }, [query]);

    return matches;
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // UPDATE DIMENSIONS
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (typeof window === 'undefined') return;

    let timeoutId: NodeJS.Timeout;

    const updateDimensions = () => {
      clearTimeout(timeoutId);

      timeoutId = setTimeout(() => {
        const width = window.innerWidth;
        const height = window.innerHeight;

        setScreenWidth(width);
        setScreenHeight(height);
        setOrientation(width > height ? 'landscape' : 'portrait');

        // Determine breakpoint
        let currentBreakpoint: Breakpoint = 'xs';
        if (width >= breakpoints['2xl']) {
          currentBreakpoint = '2xl';
        } else if (width >= breakpoints.xl) {
          currentBreakpoint = 'xl';
        } else if (width >= breakpoints.lg) {
          currentBreakpoint = 'lg';
        } else if (width >= breakpoints.md) {
          currentBreakpoint = 'md';
        } else if (width >= breakpoints.sm) {
          currentBreakpoint = 'sm';
        }
        setBreakpoint(currentBreakpoint);
      }, debounceDelay);
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    window.addEventListener('orientationchange', updateDimensions);

    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener('resize', updateDimensions);
      window.removeEventListener('orientationchange', updateDimensions);
    };
  }, [breakpoints, debounceDelay]);

  // ═══════════════════════════════════════════════════════════════════════════
  // DETECT TOUCH DEVICE
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const checkTouch = () => {
      setIsTouchDevice(
        'ontouchstart' in window ||
        navigator.maxTouchPoints > 0 ||
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (navigator as any).msMaxTouchPoints > 0
      );
    };

    checkTouch();
    window.addEventListener('touchstart', checkTouch, { once: true });

    return () => {
      window.removeEventListener('touchstart', checkTouch);
    };
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // PIXEL RATIO
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (typeof window === 'undefined') return;

    setPixelRatio(window.devicePixelRatio || 1);

    const mediaQuery = window.matchMedia(`(resolution: ${window.devicePixelRatio}dppx)`);
    
    const handler = () => {
      setPixelRatio(window.devicePixelRatio || 1);
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // PREFERENCES
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const darkQuery = window.matchMedia('(prefers-color-scheme: dark)');

    setPrefersReducedMotion(motionQuery.matches);
    setPrefersDarkMode(darkQuery.matches);

    const motionHandler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    const darkHandler = (e: MediaQueryListEvent) => setPrefersDarkMode(e.matches);

    motionQuery.addEventListener('change', motionHandler);
    darkQuery.addEventListener('change', darkHandler);

    return () => {
      motionQuery.removeEventListener('change', motionHandler);
      darkQuery.removeEventListener('change', darkHandler);
    };
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // HELPER FUNCTIONS
  // ═══════════════════════════════════════════════════════════════════════════

  const matches = useCallback(
    (query: string): boolean => {
      if (typeof window === 'undefined') return defaultMatches;
      return window.matchMedia(query).matches;
    },
    [defaultMatches]
  );

  const isBreakpoint = useCallback(
    (bp: Breakpoint): boolean => {
      return breakpoint === bp;
    },
    [breakpoint]
  );

  const isAbove = useCallback(
    (bp: Breakpoint): boolean => {
      const currentWidth = breakpoints[breakpoint];
      const targetWidth = breakpoints[bp];
      return currentWidth >= targetWidth;
    },
    [breakpoint, breakpoints]
  );

  const isBelow = useCallback(
    (bp: Breakpoint): boolean => {
      const currentWidth = breakpoints[breakpoint];
      const targetWidth = breakpoints[bp];
      return currentWidth < targetWidth;
    },
    [breakpoint, breakpoints]
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // COMPUTED VALUES
  // ═══════════════════════════════════════════════════════════════════════════

  const isMobile = breakpoint === 'xs' || breakpoint === 'sm';
  const isTablet = breakpoint === 'md';
  const isDesktop = breakpoint === 'lg' || breakpoint === 'xl' || breakpoint === '2xl';

  // ═══════════════════════════════════════════════════════════════════════════
  // RETURN
  // ═══════════════════════════════════════════════════════════════════════════

  return {
    breakpoint,
    isMobile,
    isTablet,
    isDesktop,
    matches,
    isBreakpoint,
    isAbove,
    isBelow,
    screenWidth,
    screenHeight,
    orientation,
    isTouchDevice,
    pixelRatio,
    prefersReducedMotion,
    prefersDarkMode,
  };
}

export default useMediaQuery;
