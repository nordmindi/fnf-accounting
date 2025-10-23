# Template Customization Guide

This guide will help you customize the React Native Expo Template for your specific project needs.

## 🚀 Quick Setup

Run the setup script to quickly configure your project:

```bash
node scripts/setup.js
```

This will prompt you for:
- App Name
- App Slug
- Bundle Identifier
- Author Information
- GitHub URL

## 📁 Project Structure Overview

```
src/
├── components/          # Reusable UI components
├── config/             # Configuration and design tokens
├── hooks/              # Custom React hooks
├── i18n/               # Internationalization
├── screens/            # Screen components
├── services/           # Business logic and external services
├── state/              # State management (Zustand)
├── theme/              # Theme system
├── utils/              # Utility functions
└── __tests__/          # Test files
```

## 🎨 Customizing the Design System

### Colors
Edit `src/config/colors.ts` to customize your color palette:

```typescript
export const colors = {
  primary: '#2DD4BF',     // Your primary color
  secondary: '#FF8A65',   // Your secondary color
  accent: '#FFD166',      // Your accent color
  // ... other colors
};
```

### Typography
Modify `src/config/typography.ts` to adjust font sizes and weights:

```typescript
export const typography = {
  scale: {
    h1: {
      fontSize: 32,
      fontWeight: '700',
      lineHeight: 38,
    },
    // ... other typography styles
  },
};
```

### Spacing
Update `src/config/spacing.ts` to change the spacing system:

```typescript
export const spacing = {
  xs: 4,    // 4px
  sm: 8,    // 8px
  md: 12,   // 12px
  // ... other spacing values
};
```

## 🧩 Creating Components

### Component Structure
Create new components in `src/components/` following this pattern:

```typescript
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useAppTheme } from '@/theme/provider';

interface MyComponentProps {
  title: string;
  onPress?: () => void;
}

const MyComponent: React.FC<MyComponentProps> = ({ title, onPress }) => {
  const theme = useAppTheme();
  
  const styles = StyleSheet.create({
    container: {
      backgroundColor: theme.colors.surface,
      padding: theme.spacing.lg,
    },
    text: {
      ...theme.typography.body,
      color: theme.colors.text,
    },
  });
  
  return (
    <View style={styles.container}>
      <Text style={styles.text}>{title}</Text>
    </View>
  );
};

export default MyComponent;
```

### Component Testing
Add tests for your components in `src/__tests__/components/`:

```typescript
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { ThemeProvider } from '@/theme/provider';
import MyComponent from '@/components/MyComponent';

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider mode="light">{children}</ThemeProvider>
);

describe('MyComponent', () => {
  it('renders correctly', () => {
    const { getByText } = render(
      <TestWrapper>
        <MyComponent title="Test" />
      </TestWrapper>
    );
    
    expect(getByText('Test')).toBeTruthy();
  });
});
```

## 📱 Adding Screens

### Screen Structure
Create new screens in `src/screens/`:

```typescript
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTranslation } from 'react-i18next';
import { useAppTheme } from '@/theme/provider';

const MyScreen: React.FC = () => {
  const { t } = useTranslation();
  const theme = useAppTheme();
  
  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    content: {
      flex: 1,
      padding: theme.spacing.screen.horizontal,
    },
  });
  
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text>{t('screens.myScreen.title')}</Text>
      </View>
    </SafeAreaView>
  );
};

export default MyScreen;
```

### Navigation Setup
Add your screens to the navigation in `App.tsx`:

```typescript
import MyScreen from '@/screens/MyScreen';

// Add to your navigator
<Tab.Screen 
  name="MyScreen" 
  component={MyScreen}
  options={{ title: t('navigation.myScreen') }}
/>
```

## 🌍 Internationalization

### Adding Translations
Add new translations to `src/i18n/en.json` and `src/i18n/sv.json`:

```json
{
  "screens": {
    "myScreen": {
      "title": "My Screen",
      "subtitle": "Screen description"
    }
  }
}
```

### Using Translations
Use translations in your components:

```typescript
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
  const { t } = useTranslation();
  
  return <Text>{t('screens.myScreen.title')}</Text>;
};
```

## 🗃️ State Management

### Adding State
Create new state stores in `src/state/`:

```typescript
import { create } from 'zustand';

interface MyState {
  data: string[];
  addItem: (item: string) => void;
  removeItem: (index: number) => void;
}

export const useMyStore = create<MyState>((set) => ({
  data: [],
  addItem: (item) => set((state) => ({ 
    data: [...state.data, item] 
  })),
  removeItem: (index) => set((state) => ({ 
    data: state.data.filter((_, i) => i !== index) 
  })),
}));
```

### Using State
Use state in your components:

```typescript
import { useMyStore } from '@/state/myStore';

const MyComponent = () => {
  const { data, addItem } = useMyStore();
  
  return (
    <View>
      {data.map((item, index) => (
        <Text key={index}>{item}</Text>
      ))}
    </View>
  );
};
```

## 🧪 Testing

### Running Tests
```bash
npm test                 # Run all tests
npm run test:watch      # Run tests in watch mode
npm run test:coverage   # Run tests with coverage
```

### Test Structure
Organize tests by feature:

```
src/__tests__/
├── components/         # Component tests
├── screens/           # Screen tests
├── services/          # Service tests
├── state/             # State tests
└── utils/             # Utility tests
```

## 🚀 Building and Deployment

### EAS Build Setup
1. Install EAS CLI: `npm install -g @expo/eas-cli`
2. Login: `eas login`
3. Configure: `eas build:configure`
4. Build: `eas build --platform all`

### Environment Variables
Add environment variables to your build:

```bash
eas build --platform all --env production
```

## 📚 Best Practices

### Code Organization
- Keep components small and focused
- Use TypeScript interfaces for props
- Follow the established folder structure
- Use path aliases for clean imports

### Performance
- Use `StyleSheet.create` for styles
- Implement proper memoization
- Optimize images and assets
- Use FlatList for large lists

### Accessibility
- Add proper accessibility labels
- Ensure good color contrast
- Support screen readers
- Test with accessibility tools

### Security
- Never commit sensitive data
- Use environment variables for secrets
- Validate user inputs
- Implement proper error handling

## 🔧 Troubleshooting

### Common Issues

**Metro bundler issues:**
```bash
npx expo start --clear
```

**TypeScript errors:**
```bash
npm run type-check
```

**Test failures:**
```bash
npm run test -- --verbose
```

**Build issues:**
```bash
eas build --clear-cache
```

## 📖 Additional Resources

- [Expo Documentation](https://docs.expo.dev/)
- [React Navigation](https://reactnavigation.org/)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [React Native Testing Library](https://callstack.github.io/react-native-testing-library/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

---

**Happy coding! 🎉**
