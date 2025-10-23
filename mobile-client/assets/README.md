# Assets Directory

This directory contains app assets like icons and images.

## Required Assets

For a complete app, you'll need:

- `icon.png` - App icon (1024x1024px)
- `splash.png` - Splash screen image (optional)

## Current Status

The app is configured to work without these assets for development purposes. For production builds, you'll need to add the appropriate icon files.

## Adding Icons

1. Create a 1024x1024px icon with the Fire & Forget Accounting flame logo
2. Save it as `icon.png` in this directory
3. Update `app.json` to reference the icon:

```json
{
  "expo": {
    "icon": "./assets/icon.png",
    "ios": {
      "icon": "./assets/icon.png"
    },
    "android": {
      "icon": "./assets/icon.png"
    }
  }
}
```
