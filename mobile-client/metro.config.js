const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Ensure proper module resolution
config.resolver.platforms = ['ios', 'android', 'native', 'web'];

// Enable package exports for proper module resolution
config.resolver.unstable_enablePackageExports = true;

// Add resolver source extensions
config.resolver.sourceExts = [...config.resolver.sourceExts, 'mjs'];

module.exports = config;
