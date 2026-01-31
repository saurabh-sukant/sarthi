import React, { useState } from 'react'
import Chat from './components/Chat'
import Agents from './components/Agents'
import Feedback from './components/Feedback'

export default function App() {
  const [page, setPage] = useState('chat')

  return (
    <div className="app-root">
      <nav className="app-nav">
        <button onClick={() => setPage('chat')}>Chat</button>
        <button onClick={() => setPage('agents')}>Agents</button>
        <button onClick={() => setPage('feedback')}>Feedback</button>
      </nav>
      <main className="app-main">
        {page === 'chat' && <Chat />}
        {page === 'agents' && <Agents />}
        {page === 'feedback' && <Feedback />}
      </main>
    </div>
  )
}
