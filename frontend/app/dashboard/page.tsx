import { Metadata } from 'next';
import DashboardClient from './dashboard-client';

export const metadata: Metadata = {
  title: 'DeFi Analytics Dashboard | Advanced Strategy Analysis',
  description: 'Professional DeFi analytics dashboard with AI-powered insights, risk analysis, and yield optimization tools.',
};

export default function DashboardPage() {
  return <DashboardClient />;
}
