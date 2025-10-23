# Fire & Forget Accounting Mobile Client

A React Native mobile application for the Fire & Forget Accounting system, featuring AI-powered natural language processing for expense automation.

## 🚀 Quick Start

### Prerequisites

1. **Backend Running**: Ensure the Fire & Forget Accounting backend is running on `http://localhost:8000`
2. **Node.js**: Version 18.0.0 or higher
3. **Expo CLI**: Install globally with `npm install -g @expo/cli`
4. **Mobile Device**: iOS Simulator, Android Emulator, or physical device with Expo Go app

### Installation

```bash
# Navigate to mobile client directory
cd mobile-client

# Install dependencies
npm install

# Test API connection (optional)
npm run test:api

# Start development server
npm start
```

### Running the App

1. **Expo Go (Recommended for testing)**:
   - Install Expo Go app on your mobile device
   - Scan the QR code from the terminal
   - The app will load on your device

2. **iOS Simulator**:
   ```bash
   npm run ios
   ```

3. **Android Emulator**:
   ```bash
   npm run android
   ```

4. **Web Browser**:
   ```bash
   npm run web
   ```

## 📱 Features

### Core Functionality

- **Natural Language Processing**: Input expenses in plain English
- **AI-Powered Automation**: Automatic booking creation and VAT calculation
- **Real-time Feedback**: Instant confirmation of successful bookings
- **Activity Feed**: View recent transactions and system notifications
- **Multi-language Support**: English and Swedish interfaces

### Supported Expense Types

- **Representation Meals**: Business lunches with clients
- **Taxi Transport**: Business travel expenses
- **SaaS Subscriptions**: Software and service subscriptions
- **Office Supplies**: Business equipment and supplies

### Example Inputs

```
"Business lunch with client at restaurant, 800 SEK"
"Taxi from office to client meeting, 250 SEK"
"Monthly Slack subscription, 89 SEK"
"Office supplies from IKEA, 450 SEK"
```

## 🏗️ Architecture

### Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Button.tsx      # Button with variants
│   └── Card.tsx        # Card container
├── config/             # Configuration and design tokens
│   ├── colors.ts       # Color palette
│   ├── typography.ts   # Typography system
│   ├── spacing.ts      # Spacing tokens
│   └── environment.ts  # Environment config
├── screens/            # Screen components
│   ├── FireScreen.tsx  # Main NLP interface
│   └── HomeScreen.tsx  # Placeholder screens
├── services/           # Business logic
│   └── apiService.ts   # Backend API integration
├── state/              # State management
│   ├── userStore.ts    # User state
│   └── uiStore.ts      # UI state
├── theme/              # Theme system
│   ├── provider.tsx    # Theme context
│   └── tokens.ts        # Theme tokens
└── i18n/               # Internationalization
    ├── en.json         # English translations
    └── sv.json         # Swedish translations
```

### Key Components

- **FireScreen**: Main interface for NLP expense input
- **ApiService**: Handles all backend communication
- **Theme System**: Light/dark mode with consistent design tokens
- **State Management**: Zustand for global state with persistence

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the mobile-client directory:

```env
EXPO_PUBLIC_API_URL=http://localhost:8000
```

### Backend Connection

The app connects to the backend API at `http://localhost:8000` by default. To change this:

1. Update `src/config/environment.ts`
2. Set the `EXPO_PUBLIC_API_URL` environment variable
3. Restart the development server

### API Endpoints Used

- `POST /api/v1/auth/test-token` - Get authentication token
- `POST /api/v1/natural-language/process` - Process NLP input
- `GET /api/v1/natural-language/examples` - Get example inputs
- `GET /api/v1/bookings` - Get booking history
- `GET /health` - Health check

## 🧪 Testing

### Run Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Test API connection
npm run test:api
```

### Test API Connection

Before running the mobile app, verify the backend is accessible:

```bash
npm run test:api
```

This will test:
- Health endpoints
- Authentication
- Natural language processing
- Example data retrieval

## 🎨 Design System

### Color Palette

- **Primary**: #2DD4BF (Teal)
- **Secondary**: #FF8A65 (Coral)
- **Accent**: #FFD166 (Gold)
- **Background**: #0F1724 (Dark) / #FFFFFF (Light)

### Typography

- **System Font**: Optimized for mobile readability
- **Scale**: H1 (32px) to Caption (12px)
- **Weights**: Regular (400) to Bold (700)

### Spacing

- **Base Unit**: 4px
- **Scale**: xs (4px) to 8xl (96px)
- **Touch Targets**: Minimum 44px

## 📱 Platform Support

### iOS
- **Minimum Version**: iOS 13.0
- **Bundle ID**: com.fireforget.accounting
- **Permissions**: Camera, Photo Library

### Android
- **Minimum API**: 21 (Android 5.0)
- **Package**: com.fireforget.accounting
- **Permissions**: Camera, Storage

### Web
- **Browsers**: Chrome, Firefox, Safari, Edge
- **Features**: Full functionality with responsive design

## 🚀 Deployment

### Development Build

```bash
# Build for development
eas build --profile development --platform all
```

### Production Build

```bash
# Build for production
eas build --profile production --platform all
```

### App Store Submission

```bash
# Submit to app stores
eas submit --platform ios
eas submit --platform android
```

## 🔧 Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Ensure backend is running on `http://localhost:8000`
   - Check network connectivity
   - Run `npm run test:api` to verify connection

2. **Metro Bundler Issues**
   ```bash
   npx expo start --clear
   ```

3. **TypeScript Errors**
   ```bash
   npm run type-check
   ```

4. **Build Issues**
   ```bash
   eas build --clear-cache
   ```

### Debug Mode

Enable debug logging by setting `__DEV__` to `true` in the environment configuration.

## 📚 API Integration

### Natural Language Processing

The app sends natural language input to the backend for processing:

```typescript
const response = await apiService.processNaturalLanguage({
  text: "Business lunch with client, 800 SEK",
  company_id: "123e4567-e89b-12d3-a456-426614174007"
});
```

### Response Handling

The app handles three types of responses:

- **🟢 GREEN**: Auto-booked successfully
- **🟡 YELLOW**: Requires clarification
- **🔴 RED**: Manual review needed

### Error Handling

- Network errors with retry logic
- Authentication token refresh
- Graceful fallback for offline mode

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: [Backend API Docs](../docs/API.md)
- **Issues**: [GitHub Issues](https://github.com/fireforget/accounting/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fireforget/accounting/discussions)

---

**Built with ❤️ using React Native, Expo, and TypeScript**