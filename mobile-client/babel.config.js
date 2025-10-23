module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      [
        'module-resolver',
        {
          root: ['./src'],
          alias: {
            '@': './src',
            '@/components': './src/components',
            '@/screens': './src/screens',
            '@/state': './src/state',
            '@/config': './src/config',
            '@/utils': './src/utils',
            '@/i18n': './src/i18n',
            '@/hooks': './src/hooks',
            '@/services': './src/services',
            '@/theme': './src/theme',
          },
        },
      ],
    ],
  };
};
