
import React, { useState } from 'react'
import Chat from './components/Chat'
import Agents from './components/Agents'
import Feedback from './components/Feedback'
import ExecutionStream from './components/ExecutionStream'
import styles from './App.module.css'

const getIconColor = (isActive) => isActive ? '#2563eb' : '#64748b'

const createNavIcon = (isActive, type) => {
  const color = getIconColor(isActive)
  const iconProps = { width: '24', height: '24', viewBox: '0 0 24 24', fill: 'none' }
  
  if (type === 'chat') return <svg {...iconProps}><rect x="3" y="5" width="18" height="14" rx="3" stroke={color} strokeWidth="2"/><path d="M7 9h10M7 13h6" stroke={color} strokeWidth="2" strokeLinecap="round"/></svg>
  if (type === 'memory') return <svg {...iconProps}><rect x="4" y="7" width="16" height="10" rx="2" stroke={color} strokeWidth="2"/><path d="M8 11h8" stroke={color} strokeWidth="2" strokeLinecap="round"/></svg>
  if (type === 'knowledge') return <svg {...iconProps}><rect x="5" y="4" width="14" height="16" rx="2" stroke={color} strokeWidth="2"/><path d="M9 8h6M9 12h6M9 16h6" stroke={color} strokeWidth="2" strokeLinecap="round"/></svg>
  if (type === 'health') return <svg {...iconProps}><circle cx="12" cy="12" r="9" stroke={color} strokeWidth="2"/><path d="M8 12h2l2 4 2-8h2" stroke={color} strokeWidth="2" strokeLinecap="round"/></svg>
}

const navItems = [
  { key: 'chat', label: 'Incident Console', type: 'chat' },
  { key: 'memory', label: 'Memory Bank', type: 'memory' },
  { key: 'knowledge', label: 'Knowledge Base', type: 'knowledge' },
  { key: 'health', label: 'System Health', type: 'health' },
]

export default function App() {
  const [page, setPage] = useState('chat')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [executionId, setExecutionId] = useState(null)
  const [chatWidth, setChatWidth] = useState(50) // percentage
  const [isResizing, setIsResizing] = useState(false)

  const handleMouseDown = () => {
    setIsResizing(true)
  }

  const handleMouseUp = () => {
    setIsResizing(false)
  }

  const handleMouseMove = (e) => {
    if (!isResizing) return
    const mainElement = document.querySelector('[data-app-main]')
    if (!mainElement) return
    const rect = mainElement.getBoundingClientRect()
    const newWidth = ((e.clientX - rect.left) / rect.width) * 100
    // Constrain width between 30% and 70%
    if (newWidth >= 30 && newWidth <= 70) {
      setChatWidth(newWidth)
    }
  }

  React.useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
      return () => {
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isResizing])

  return (
    <div className={styles['app-root']}>
      <nav className={`${styles['app-nav']} ${sidebarCollapsed ? styles['collapsed'] : ''}`}>
        <div className={styles['nav-header']}>
          <div className={styles['nav-header-content']}>
            <div className={styles['nav-header-icon']}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" />
                <path d="M12 12v4m-2-2h4" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            {!sidebarCollapsed && <div className={styles['nav-header-name']}>SARTHI</div>}
          </div>
        </div>
        <button
          className={styles['nav-toggle']}
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          title={sidebarCollapsed ? 'Expand' : 'Collapse'}
          aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {sidebarCollapsed ? '→' : '←'}
        </button>
        <div className={styles['nav-items']}>
          {navItems.map(item => (
            <button
              key={item.key}
              className={page === item.key ? 'active' : ''}
              onClick={() => setPage(item.key)}
              title={item.label}
              aria-label={item.label}
            >
              {createNavIcon(page === item.key, item.type)}
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </nav>
      <main className={`${styles['app-main']} ${sidebarCollapsed ? styles['collapsed'] : ''}`} data-app-main>
        {page === 'chat' && (
          <div style={{ display: 'flex', width: '100%', height: '100%' }}>
            <div style={{ width: `${chatWidth}%`, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Chat onExecutionStart={(id) => setExecutionId(id)} />
            </div>
            <div
              className={styles['resize-divider']}
              onMouseDown={handleMouseDown}
              style={{ cursor: isResizing ? 'col-resize' : 'default' }}
              title="Drag to resize"
            />
            <div style={{ width: `${100 - chatWidth}%`, height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <ExecutionStream executionId={executionId} />
            </div>
          </div>
        )}
        {page === 'memory' && <Agents />}
        {page === 'knowledge' && <Feedback />}
        {page === 'health' && (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94a3b8', fontSize: 24, background: '#F8FAFC' }}>
            <span>System Health Dashboard (Coming Soon)</span>
          </div>
        )}
      </main>
    </div>
  )
}
