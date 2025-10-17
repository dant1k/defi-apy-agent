'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

export function Navigation() {
  const pathname = usePathname();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className={`sidebar-genora ${sidebarCollapsed ? 'collapsed' : ''}`}>
      {/* Logo and App Name */}
      <div className="sidebar-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="logo-icon-artemis">
              <img 
                src="/icon-lamp-transparent.png" 
                alt="Genora Lamp" 
                className="logo-image-artemis"
              />
            </div>
            <span className="app-name-artemis">Genora</span>
          </div>
          
          {/* Sidebar Toggle Button - appears on hover when expanded */}
          {!sidebarCollapsed && (
            <button 
              className="sidebar-collapse-btn"
              onClick={() => setSidebarCollapsed(true)}
              title="Collapse menu"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M15 18l-6-6 6-6"/>
              </svg>
            </button>
          )}
        </div>
        
        {/* Expand Button - appears on hover when collapsed */}
        {sidebarCollapsed && (
          <button 
            className="sidebar-expand-btn"
            onClick={() => setSidebarCollapsed(false)}
            title="Expand menu"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </button>
        )}
      </div>

      {/* Search Bar */}
      <div className="search-container">
        <div className="search-input">
          <svg className="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          <input type="text" placeholder="Search..." className="search-field" />
          <div className="search-shortcut">⌘K</div>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="nav-sections">
        <Link 
          href="/" 
          className={`nav-item ${pathname === '/' ? 'nav-item-active' : ''}`}
        >
          <svg className="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9,22 9,12 15,12 15,22"/>
          </svg>
          <span>Analytics Dashboard</span>
        </Link>

        <Link 
          href="/strategies" 
          className={`nav-item ${pathname === '/strategies' ? 'nav-item-active' : ''}`}
        >
          <svg className="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 3h18v18H3zM9 9h6v6H9z"/>
            <path d="M9 3v6M15 3v6M9 15v6M15 15v6"/>
          </svg>
          <span>Strategies</span>
        </Link>
      </div>
    </div>
  );
}
