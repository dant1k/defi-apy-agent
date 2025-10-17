'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="nav-genora">
      <div className="flex items-center justify-between">
        <Link href="/" className="font-orbitron text-xl font-bold text-white">
          Genora
        </Link>
        
        <div className="flex items-center space-x-6">
          <Link 
            href="/" 
            className={`font-inter font-medium transition-colors ${
              pathname === '/' 
                ? 'text-[var(--neonAqua)]' 
                : 'text-white/75 hover:text-[var(--neonAqua)]'
            }`}
          >
            Analytics Dashboard
          </Link>
          <Link 
            href="/strategies" 
            className={`font-inter font-medium transition-colors ${
              pathname === '/strategies' 
                ? 'text-[var(--neonAqua)]' 
                : 'text-white/75 hover:text-[var(--neonAqua)]'
            }`}
          >
            Strategies
          </Link>
        </div>
      </div>
    </nav>
  );
}
