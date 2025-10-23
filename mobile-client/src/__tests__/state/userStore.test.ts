/**
 * User Store Tests
 */

import { renderHook, act } from '@testing-library/react-native';
import { useUserStore } from '@/state/userStore';

describe('User Store', () => {
  beforeEach(() => {
    // Reset store state before each test
    useUserStore.getState().resetProgress();
  });

  it('initializes with default values', () => {
    const { result } = renderHook(() => useUserStore());
    
    expect(result.current.progress.nickname).toBe('');
    expect(result.current.progress.language).toBe('en');
    expect(result.current.progress.theme).toBe('auto');
    expect(result.current.progress.totalXp).toBe(0);
    expect(result.current.progress.currentLevel).toBe(1);
  });

  it('updates nickname correctly', () => {
    const { result } = renderHook(() => useUserStore());
    
    act(() => {
      result.current.updateNickname('Test User');
    });
    
    expect(result.current.progress.nickname).toBe('Test User');
  });

  it('updates language correctly', () => {
    const { result } = renderHook(() => useUserStore());
    
    act(() => {
      result.current.updateLanguage('sv');
    });
    
    expect(result.current.progress.language).toBe('sv');
  });

  it('updates theme correctly', () => {
    const { result } = renderHook(() => useUserStore());
    
    act(() => {
      result.current.updateTheme('dark');
    });
    
    expect(result.current.progress.theme).toBe('dark');
  });

  it('resets progress correctly', () => {
    const { result } = renderHook(() => useUserStore());
    
    // First, update some values
    act(() => {
      result.current.updateNickname('Test User');
      result.current.updateLanguage('sv');
    });
    
    // Then reset
    act(() => {
      result.current.resetProgress();
    });
    
    expect(result.current.progress.nickname).toBe('');
    expect(result.current.progress.language).toBe('en');
  });

  it('exports data correctly', () => {
    const { result } = renderHook(() => useUserStore());
    
    act(() => {
      result.current.updateNickname('Test User');
    });
    
    const exportedData = result.current.exportData();
    const parsedData = JSON.parse(exportedData);
    
    expect(parsedData.nickname).toBe('Test User');
  });
});
