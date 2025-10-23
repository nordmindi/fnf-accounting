#!/usr/bin/env node

/**
 * Setup script for the React Native Expo Template
 * This script helps customize the template for your specific project
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

function question(query) {
  return new Promise((resolve) => rl.question(query, resolve));
}

async function setup() {
  console.log('🚀 Welcome to the React Native Expo Template Setup!');
  console.log('This script will help you customize the template for your project.\n');

  try {
    // Get project information
    const appName = await question('📱 App Name: ');
    const appSlug = await question('🔗 App Slug (lowercase, no spaces): ');
    const bundleId = await question('📦 Bundle Identifier (com.yourcompany.yourapp): ');
    const authorName = await question('👤 Author Name: ');
    const authorEmail = await question('📧 Author Email: ');
    const githubUrl = await question('🐙 GitHub URL (optional): ');

    console.log('\n🔄 Updating configuration files...');

    // Update package.json
    const packageJsonPath = path.join(__dirname, '..', 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    
    packageJson.name = appSlug;
    packageJson.description = `${appName} - A React Native app built with Expo and TypeScript`;
    packageJson.author = `${authorName} <${authorEmail}>`;
    if (githubUrl) {
      packageJson.homepage = githubUrl;
    }

    fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));

    // Update app.json
    const appJsonPath = path.join(__dirname, '..', 'app.json');
    const appJson = JSON.parse(fs.readFileSync(appJsonPath, 'utf8'));
    
    appJson.expo.name = appName;
    appJson.expo.slug = appSlug;
    appJson.expo.ios.bundleIdentifier = bundleId;
    appJson.expo.android.package = bundleId;
    appJson.expo.description = `${appName} - A production-ready React Native app built with Expo and TypeScript.`;
    if (githubUrl) {
      appJson.expo.githubUrl = githubUrl;
    }

    fs.writeFileSync(appJsonPath, JSON.stringify(appJson, null, 2));

    // Update README.md
    const readmePath = path.join(__dirname, '..', 'README.md');
    let readme = fs.readFileSync(readmePath, 'utf8');
    
    readme = readme.replace(/Your App Name/g, appName);
    readme = readme.replace(/your-app/g, appSlug);
    readme = readme.replace(/yourusername/g, authorName.toLowerCase());
    readme = readme.replace(/your.email@example.com/g, authorEmail);

    fs.writeFileSync(readmePath, readme);

    // Update environment config
    const envConfigPath = path.join(__dirname, '..', 'src', 'config', 'environment.ts');
    let envConfig = fs.readFileSync(envConfigPath, 'utf8');
    
    envConfig = envConfig.replace(/Your App Name/g, appName);
    envConfig = envConfig.replace(/1\.0\.0/g, '1.0.0');

    fs.writeFileSync(envConfigPath, envConfig);

    console.log('✅ Configuration files updated successfully!');
    console.log('\n📋 Next steps:');
    console.log('1. Run `npm install` to install dependencies');
    console.log('2. Run `npm start` to start the development server');
    console.log('3. Update the app icon in the assets folder');
    console.log('4. Customize the design system in src/config/');
    console.log('5. Add your screens in src/screens/');
    console.log('6. Update translations in src/i18n/');
    console.log('\n🎉 Happy coding!');

  } catch (error) {
    console.error('❌ Error during setup:', error.message);
  } finally {
    rl.close();
  }
}

setup();
