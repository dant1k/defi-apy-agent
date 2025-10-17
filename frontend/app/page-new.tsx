import { Metadata } from 'next';
import DashboardClient from './dashboard/dashboard-client';

export const metadata: Metadata = {
  title: 'DeFi Analytics Dashboard | DeFi APY Agent',
  description: 'Professional DeFi analytics dashboard with AI-powered insights, risk analysis, and yield optimization tools.',
};

export default function HomePage() {
  return <DashboardClient />;
}
