import React, { useState, useEffect } from 'react'
import { submitChatQuery, createEventSource } from '../services/api'

export default function Chat() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    { id: 'welcome', role: 'assistant', text: 'Hello — ask me about incidents or system issues.' },
  ])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    return () => {
      // cleanup if needed
    }
  }, [])

  async function send() {
    if (!input.trim()) return
    const text = input.trim()
    setMessages((m) => [...m, { id: Date.now(), role: 'user', text }])
    setInput('')
    setLoading(true)

    try {
      const res = await submitChatQuery(text)
      if (res.execution_id) {
        const es = createEventSource(res.execution_id)
        es.onmessage = (ev) => {
          try {
            const d = JSON.parse(ev.data)
            // Accept both 'final_response' and 'response' fields from SSE
            const answer = d.final_response || d.response || d.answer
            if ((d.event === 'final_response' || d.type === 'response' || d.status === 'completed') && answer) {
              setMessages((m) => [...m, { id: Date.now() + 1, role: 'assistant', text: answer }])
              es.close()
              setLoading(false)
            }
          } catch (e) {
            // ignore parse errors
          }
        }
        es.onerror = () => {
          es.close()
          setLoading(false)
        }
      } else if (res.response) {
        setMessages((m) => [...m, { id: Date.now() + 2, role: 'assistant', text: res.response }])
      } else if (res.answer) {
        setMessages((m) => [...m, { id: Date.now() + 2, role: 'assistant', text: res.answer }])
      }
    } catch (err) {
      setMessages((m) => [...m, { id: Date.now() + 3, role: 'assistant', text: 'Error: failed to send query' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-root">
      <div className="messages">
        {messages.map((m) => (
          <div key={m.id} className={`message ${m.role}`}>
            <div className="message-role">{m.role}</div>
            <div className="message-text">{m.text}</div>
          </div>
        ))}
      </div>

      <div className="chat-input">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) send() }}
          placeholder="Ask SARTHI..."
        />
        <button onClick={send} disabled={loading}>{loading ? '...' : 'Send'}</button>
      </div>
    </div>
  )
}
