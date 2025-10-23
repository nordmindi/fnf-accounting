# React Native Expo Template

A production-ready React Native template based on the Unstuck Quest architecture, featuring a comprehensive design system, state management, testing setup, and modern development practices.

## 🚀 **Quick Start**

```bash
# Clone this template
git clone <template-repo-url> my-app
cd my-app

# Install dependencies
npm install

# Start development
npm start
```

## 📋 **What's Included**

### **🏗️ Architecture**
- **Clean Architecture**: Separation of concerns with clear folder structure
- **TypeScript**: Full TypeScript support with strict configuration
- **Path Aliases**: Clean imports with `@/` aliases
- **Modular Structure**: Organized by feature and concern

### **🎨 Design System**
- **Comprehensive Design Tokens**: Colors, typography, spacing, shadows
- **Theme System**: Light/dark mode with automatic system detection
- **Component Library**: Reusable, accessible components
- **Consistent Styling**: 4px base unit system for harmonious layouts

### **📱 Core Features**
- **Navigation**: React Navigation with bottom tabs and stack navigation
- **State Management**: Zustand with persistence and TypeScript
- **Internationalization**: i18next with English/Swedish support
- **Notifications**: Expo notifications with scheduling
- **Sound System**: Audio feedback with haptic responses
- **Storage**: AsyncStorage with proper error handling

### **🧪 Testing**
- **Jest Configuration**: Comprehensive test setup
- **React Native Testing Library**: Component testing utilities
- **Mocking**: Proper mocks for native modules
- **Coverage**: 70% coverage thresholds
- **Test Structure**: Organized test files with clear naming

### **🛠️ Development Tools**
- **ESLint**: Code quality and consistency
- **Prettier**: Code formatting
- **TypeScript**: Type safety and IntelliSense
- **Metro**: Optimized bundling
- **Babel**: Module resolution and transformations

### **📦 Build & Deploy**
- **EAS Build**: Expo Application Services integration
- **Environment Config**: Development, staging, production configs
- **App Store Ready**: Proper configuration for iOS/Android stores
- **CI/CD Ready**: GitHub Actions compatible

## 📁 **Project Structure**

```
src/
├── components/          # Reusable UI components
│   ├── Button.tsx      # Button component with variants
│   ├── Card.tsx        # Card component with theming
│   └── ...
├── config/             # Configuration and constants
│   ├── colors.ts       # Color palette and theme colors
│   ├── typography.ts   # Typography system
│   ├── spacing.ts      # Spacing and layout tokens
│   ├── types.ts        # TypeScript type definitions
│   └── ...
├── hooks/              # Custom React hooks
│   ├── useTheme.ts     # Theme management hook
│   └── ...
├── i18n/               # Internationalization
│   ├── en.json         # English translations
│   ├── sv.json         # Swedish translations
│   └── index.ts        # i18n configuration
├── screens/            # Screen components
│   ├── HomeScreen.tsx  # Main screens
│   └── ...
├── services/           # Business logic and external services
│   ├── notificationService.ts
│   ├── soundService.ts
│   └── ...
├── state/              # State management
│   ├── userStore.ts    # User state with Zustand
│   ├── uiStore.ts      # UI state management
│   └── index.ts        # Store exports
├── theme/              # Theme system
│   ├── provider.tsx    # Theme context provider
│   └── tokens.ts       # Theme tokens
├── utils/              # Utility functions
│   ├── storage.ts      # Storage utilities
│   └── ...
└── __tests__/          # Test files
    ├── components/     # Component tests
    ├── services/       # Service tests
    └── ...
```

## 🎨 **Design System**

### **Color Palette**
```typescript
// Brand colors
navy: '#0F1724'     // Deep Navy
teal: '#2DD4BF'     // Teal Mint
coral: '#FF8A65'    // Warm Coral
gold: '#FFD166'     // Gold

// Theme-aware colors
light: {
  background: '#FFFFFF',
  surface: '#F8FAFC',
  text: '#0F1724',
  textSecondary: '#475569',
  border: '#E2E8F0',
}

dark: {
  background: '#0F1724',
  surface: '#1E293B',
  text: '#F8FAFC',
  textSecondary: '#CBD5E1',
  border: '#334155',
}
```

### **Typography Scale**
```typescript
h1: { fontSize: 32, fontWeight: '700', lineHeight: 38 }
h2: { fontSize: 24, fontWeight: '600', lineHeight: 30 }
h3: { fontSize: 20, fontWeight: '600', lineHeight: 26 }
body: { fontSize: 16, fontWeight: '400', lineHeight: 24 }
button: { fontSize: 16, fontWeight: '600', lineHeight: 20 }
```

### **Spacing System**
```typescript
// 4px base unit system
xs: 4px, sm: 8px, md: 12px, lg: 16px, xl: 20px
2xl: 24px, 3xl: 32px, 4xl: 40px, 5xl: 48px
```

## 🧩 **Component Usage**

### **Button Component**
```typescript
import { Button } from '@/components/Button';

<Button
  title="Click me"
  onPress={() => console.log('Pressed')}
  variant="primary"
  size="medium"
  disabled={false}
/>
```

### **Card Component**
```typescript
import { Card } from '@/components/Card';

<Card style={styles.card}>
  <Text>Card content</Text>
</Card>
```

### **Theme Usage**
```typescript
import { useAppTheme } from '@/theme/provider';
import { useTheme } from '@/hooks/useTheme';

const MyComponent = () => {
  const theme = useAppTheme();
  const { isDark } = useTheme();
  
  const styles = StyleSheet.create({
    container: {
      backgroundColor: theme.colors.background,
      padding: theme.spacing.lg,
    },
  });
  
  return <View style={styles.container} />;
};
```

## 🧪 **Testing**

### **Component Testing**
```typescript
import { render, fireEvent } from '@testing-library/react-native';
import { Button } from '@/components/Button';

test('Button calls onPress when pressed', () => {
  const onPress = jest.fn();
  const { getByText } = render(
    <Button title="Test" onPress={onPress} />
  );
  
  fireEvent.press(getByText('Test'));
  expect(onPress).toHaveBeenCalled();
});
```

### **State Testing**
```typescript
import { useUserStore } from '@/state';

test('User store updates correctly', () => {
  const { result } = renderHook(() => useUserStore());
  
  act(() => {
    result.current.updateNickname('Test User');
  });
  
  expect(result.current.progress.nickname).toBe('Test User');
});
```

## 🌍 **Internationalization**

### **Adding Translations**
```typescript
// src/i18n/en.json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel"
  },
  "screens": {
    "home": {
      "title": "Welcome"
    }
  }
}

// Usage in components
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
  const { t } = useTranslation();
  
  return <Text>{t('screens.home.title')}</Text>;
};
```

## 🔧 **Configuration**

### **Environment Variables**
```typescript
// src/config/environment.ts
export const config = {
  apiUrl: process.env.EXPO_PUBLIC_API_URL || 'https://api.example.com',
  isDev: __DEV__,
  version: '1.0.0',
};
```

### **TypeScript Configuration**
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@/components/*": ["src/components/*"]
    }
  }
}
```

## 📱 **Platform-Specific Features**

### **iOS Configuration**
```json
{
  "ios": {
    "supportsTablet": true,
    "bundleIdentifier": "com.yourcompany.yourapp",
    "infoPlist": {
      "NSCameraUsageDescription": "Camera access description"
    }
  }
}
```

### **Android Configuration**
```json
{
  "android": {
    "package": "com.yourcompany.yourapp",
    "permissions": ["CAMERA", "NOTIFICATIONS"]
  }
}
```

## 🚀 **Deployment**

### **EAS Build**
```bash
# Install EAS CLI
npm install -g @expo/eas-cli

# Configure project
eas build:configure

# Build for production
eas build --platform all
```

### **App Store Submission**
```bash
# Submit to stores
eas submit --platform ios
eas submit --platform android
```

## 📚 **Best Practices**

### **Code Organization**
- Keep components small and focused
- Use TypeScript interfaces for props
- Follow the established folder structure
- Use path aliases for clean imports

### **State Management**
- Use Zustand for global state
- Keep local state in components when possible
- Use computed values for derived state
- Persist important state to storage

### **Styling**
- Use the design system tokens
- Make components theme-aware
- Follow the spacing system
- Use StyleSheet.create for performance

### **Testing**
- Write tests for business logic
- Test user interactions
- Mock external dependencies
- Maintain good test coverage

## 🔄 **Migration Guide**

### **From Existing Projects**
1. Copy the `src/` folder structure
2. Update `package.json` dependencies
3. Configure TypeScript paths
4. Set up testing environment
5. Migrate existing components

### **Customization**
1. Update color palette in `src/config/colors.ts`
2. Modify typography in `src/config/typography.ts`
3. Adjust spacing in `src/config/spacing.ts`
4. Customize components in `src/components/`
5. Update translations in `src/i18n/`

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details

## 🆘 **Support**

- **Documentation**: [Link to docs]
- **Issues**: [GitHub Issues]
- **Discussions**: [GitHub Discussions]

---

**Built with ❤️ using React Native, Expo, and TypeScript**
