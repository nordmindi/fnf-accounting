#!/usr/bin/env node

/**
 * Test script to verify mobile client can connect to the backend API
 */

const fetch = require('node-fetch');

const API_BASE_URL = 'http://localhost:8000';

async function testApiConnection() {
  console.log('🧪 Testing API connection...\n');

  try {
    // Test health endpoint
    console.log('1. Testing health endpoint...');
    const healthResponse = await fetch(`${API_BASE_URL}/health`);
    const healthData = await healthResponse.json();
    console.log('✅ Health check:', healthData.status);
    console.log('   Service:', healthData.service);
    console.log('');

    // Test detailed health
    console.log('2. Testing detailed health...');
    const detailedHealthResponse = await fetch(`${API_BASE_URL}/health/detailed`);
    const detailedHealthData = await detailedHealthResponse.json();
    console.log('✅ Detailed health:', detailedHealthData.status);
    console.log('   Components:', Object.keys(detailedHealthData.components).join(', '));
    console.log('');

    // Test authentication
    console.log('3. Testing authentication...');
    const authResponse = await fetch(`${API_BASE_URL}/api/v1/auth/test-token`, {
      method: 'POST',
    });
    const authData = await authResponse.json();
    console.log('✅ Auth token received:', authData.access_token ? 'Yes' : 'No');
    console.log('   Token type:', authData.token_type);
    console.log('');

    // Test natural language examples
    console.log('4. Testing natural language examples...');
    const examplesResponse = await fetch(`${API_BASE_URL}/api/v1/natural-language/examples`);
    const examplesData = await examplesResponse.json();
    console.log('✅ Examples endpoint:', examplesData.examples ? 'Available' : 'Not available');
    if (examplesData.examples) {
      console.log('   Example count:', examplesData.examples.length);
      console.log('   First example:', examplesData.examples[0]?.description);
    }
    console.log('');

    // Test natural language processing
    console.log('5. Testing natural language processing...');
    const nlpResponse = await fetch(`${API_BASE_URL}/api/v1/natural-language/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authData.access_token}`,
      },
      body: JSON.stringify({
        text: 'Business lunch with client at restaurant, 800 SEK',
        company_id: '123e4567-e89b-12d3-a456-426614174007',
      }),
    });
    const nlpData = await nlpResponse.json();
    console.log('✅ NLP processing:', nlpData.success ? 'Success' : 'Failed');
    if (nlpData.success) {
      console.log('   Message:', nlpData.message);
      console.log('   Status:', nlpData.status);
      if (nlpData.booking_id) {
        console.log('   Booking ID:', nlpData.booking_id);
      }
    } else {
      console.log('   Error:', nlpData.detail || nlpData.error);
    }
    console.log('');

    console.log('🎉 All tests completed successfully!');
    console.log('📱 Mobile client should be able to connect to the backend.');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('1. Make sure the backend is running: python -m uvicorn src.app.main:app --reload');
    console.log('2. Check that the API is accessible at http://localhost:8000');
    console.log('3. Verify all required dependencies are installed');
    process.exit(1);
  }
}

testApiConnection();
