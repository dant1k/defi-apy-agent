'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="main-navigation">
      <div className="nav-container">
        <Link href="/" className="nav-logo">
          DeFi APY Agent
        </Link>
        
        <div className="nav-links">
          <Link 
            href="/" 
            className={`nav-link ${pathname === '/' ? 'active' : ''}`}
          >
            Analytics Dashboard
          </Link>
          <Link 
            href="/strategies" 
            className={`nav-link ${pathname === '/strategies' ? 'active' : ''}`}
          >
            Strategies
          </Link>
        </div>
      </div>
    </nav>
  );
}
