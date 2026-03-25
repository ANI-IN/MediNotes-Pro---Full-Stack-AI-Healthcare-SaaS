/**
 * Frontend component tests for MediNotes Pro landing page.
 *
 * Setup:
 *   npm install --save-dev jest @testing-library/react @testing-library/jest-dom ts-jest @types/jest
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

jest.mock('@clerk/nextjs', () => ({
  ClerkProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  SignInButton: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  SignedIn: ({ children }: { children: React.ReactNode }) => <div data-testid="signed-in">{children}</div>,
  SignedOut: ({ children }: { children: React.ReactNode }) => <div data-testid="signed-out">{children}</div>,
  UserButton: () => <div data-testid="user-button">UserButton</div>,
  Protect: ({ children }: { children: React.ReactNode; fallback: React.ReactNode }) => (
    <div data-testid="protect">{children}</div>
  ),
  PricingTable: () => <div data-testid="pricing-table">PricingTable</div>,
  useAuth: () => ({ getToken: jest.fn().mockResolvedValue('mock-jwt-token') }),
}));

jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
});

import Home from '../../../pages/index';

describe('Landing Page', () => {
  test('renders the app title', () => {
    render(<Home />);
    expect(screen.getByText('MediNotes Pro')).toBeInTheDocument();
  });

  test('renders the hero heading', () => {
    render(<Home />);
    expect(screen.getByText(/Transform Your/)).toBeInTheDocument();
    expect(screen.getByText(/Consultation Notes/)).toBeInTheDocument();
  });

  test('renders all three feature cards', () => {
    render(<Home />);
    expect(screen.getByText('Professional Summaries')).toBeInTheDocument();
    expect(screen.getByText('Action Items')).toBeInTheDocument();
    expect(screen.getByText('Patient Emails')).toBeInTheDocument();
  });

  test('renders sign-in section for unauthenticated users', () => {
    render(<Home />);
    const signedOutSections = screen.getAllByTestId('signed-out');
    expect(signedOutSections.length).toBeGreaterThan(0);
  });

  test('contains link to product page', () => {
    render(<Home />);
    const appLinks = screen.getAllByText('Go to App');
    const links = appLinks.map((el) => el.closest('a'));
    const productLink = links.find((link) => link?.getAttribute('href') === '/product');
    expect(productLink).toBeTruthy();
  });
});
