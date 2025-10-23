// Global mock for expo-av to avoid native module in Jest
jest.mock('expo-av', () => {
  const createAsync = async () => ({
    sound: {
      setVolumeAsync: jest.fn(),
      replayAsync: jest.fn(),
      unloadAsync: jest.fn(),
    },
  });
  return {
    Audio: {
      setAudioModeAsync: jest.fn(),
      Sound: {
        createAsync,
      },
    },
  };
});

// Mock AsyncStorage for Jest environment
jest.mock('@react-native-async-storage/async-storage', () => {
  let store: Record<string, string> = {};
  return {
    setItem: jest.fn(async (k: string, v: string) => {
      store[k] = v;
    }),
    getItem: jest.fn(async (k: string) => store[k] ?? null),
    removeItem: jest.fn(async (k: string) => {
      delete store[k];
    }),
    clear: jest.fn(async () => {
      store = {};
    }),
  };
});

// Mock expo-notifications
jest.mock('expo-notifications', () => ({
  scheduleNotificationAsync: jest.fn(),
  cancelAllScheduledNotificationsAsync: jest.fn(),
  setNotificationHandler: jest.fn(),
  getPermissionsAsync: jest.fn(() => Promise.resolve({ status: 'granted' })),
  requestPermissionsAsync: jest.fn(() => Promise.resolve({ status: 'granted' })),
}));

// Mock react-native-safe-area-context
jest.mock('react-native-safe-area-context', () => ({
  SafeAreaProvider: ({ children }: { children: React.ReactNode }) => children,
  SafeAreaView: ({ children }: { children: React.ReactNode }) => children,
  useSafeAreaInsets: () => ({ top: 0, bottom: 0, left: 0, right: 0 }),
}));
