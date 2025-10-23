/**
 * Button Component Tests
 */

import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { ThemeProvider } from '@/theme/provider';
import Button from '@/components/Button';

// Mock the theme provider for testing
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider mode="light">{children}</ThemeProvider>
);

describe('Button Component', () => {
  it('renders correctly with default props', () => {
    const { getByText } = render(
      <TestWrapper>
        <Button title="Test Button" onPress={() => {}} />
      </TestWrapper>
    );
    
    expect(getByText('Test Button')).toBeTruthy();
  });

  it('calls onPress when pressed', () => {
    const onPress = jest.fn();
    const { getByText } = render(
      <TestWrapper>
        <Button title="Test Button" onPress={onPress} />
      </TestWrapper>
    );
    
    fireEvent.press(getByText('Test Button'));
    expect(onPress).toHaveBeenCalledTimes(1);
  });

  it('does not call onPress when disabled', () => {
    const onPress = jest.fn();
    const { getByText } = render(
      <TestWrapper>
        <Button title="Test Button" onPress={onPress} disabled />
      </TestWrapper>
    );
    
    fireEvent.press(getByText('Test Button'));
    expect(onPress).not.toHaveBeenCalled();
  });

  it('shows loading indicator when loading', () => {
    const { getByTestId } = render(
      <TestWrapper>
        <Button title="Test Button" onPress={() => {}} loading />
      </TestWrapper>
    );
    
    // ActivityIndicator should be present when loading
    expect(getByTestId('activity-indicator')).toBeTruthy();
  });

  it('renders different variants correctly', () => {
    const { getByText: getPrimary } = render(
      <TestWrapper>
        <Button title="Primary" onPress={() => {}} variant="primary" />
      </TestWrapper>
    );
    
    const { getByText: getSecondary } = render(
      <TestWrapper>
        <Button title="Secondary" onPress={() => {}} variant="secondary" />
      </TestWrapper>
    );
    
    expect(getPrimary('Primary')).toBeTruthy();
    expect(getSecondary('Secondary')).toBeTruthy();
  });
});
