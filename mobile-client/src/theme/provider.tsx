import React, { createContext, useContext, useMemo } from 'react';
import { useColorScheme } from 'react-native';
import { getTheme, AppTheme, ThemeMode } from './tokens';

const ThemeContext = createContext<AppTheme | null>(null);

export const useAppTheme = (): AppTheme => {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('ThemeProvider is missing');
  return ctx;
};

export const ThemeProvider: React.FC<{ mode?: ThemeMode; children: React.ReactNode }> = ({ mode, children }) => {
  const scheme = useColorScheme();
  const resolvedMode: ThemeMode = mode || (scheme === 'dark' ? 'dark' : 'light');
  const theme = useMemo(() => getTheme(resolvedMode), [resolvedMode]);
  return <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>;
};
