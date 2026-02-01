import React, { useEffect, useState, useRef } from 'react'
import styles from './ExecutionStream.module.css'
import { createEventSource } from '../services/api'

function AgentBadge({ status }) {
  if (status === 'active') return <span className={styles['badge'] + ' ' + styles['pulse-blue']}>● Active</span>
  if (status === 'completed') return <span className={styles['badge'] + ' ' + styles['check-green']}>✓ Done</span>
  return <span className={styles['badge']}>⊙ Pending</span>
}

export default function ExecutionStream({ executionId }) {
  const [agents, setAgents] = useState([]) // [{ name, status, time, messages: [] }]
  const [finalResponse, setFinalResponse] = useState(null)
  const esRef = useRef(null)

  useEffect(() => {
    // cleanup any existing EventSource
    if (esRef.current) {
      esRef.current.close()
      esRef.current = null
    }
    setAgents([])
    setFinalResponse(null)

    if (!executionId) return

    const es = createEventSource(executionId)
    esRef.current = es

    es.onmessage = (ev) => {
      try {
        const d = JSON.parse(ev.data)
        // connected event
        if (d.event === 'connected') return

        // final response message
        if ((d.type === 'response' || d.event === 'final_response' || d.status === 'completed') && (d.final_response || d.response)) {
          setFinalResponse(d.final_response || d.response)
          return
        }

        // agent events
        const agentName = d.agent || d.agent_name || 'agent'
        const message = d.message || d.msg || ''
        const timestamp = d.timestamp || new Date().toISOString()

        setAgents((prev) => {
          const found = prev.find((p) => p.name === agentName)
          if (found) {
            return prev.map((p) => p.name === agentName ? { ...p, status: 'active', time: timestamp, messages: [...p.messages, { ts: timestamp, text: message }] } : p)
          }
          // new agent node
          return [...prev, { name: agentName, status: 'active', time: timestamp, messages: [{ ts: timestamp, text: message }] }]
        })
      } catch (err) {
        console.error('parse sse', err)
      }
    }

    es.onerror = (ev) => {
      // If server indicates completion in a separate event, it may be handled above
      // Close on error to avoid leaking connections
      try { es.close() } catch (e) {}
      esRef.current = null
    }

    return () => {
      try { es.close() } catch (e) {}
      esRef.current = null
    }
  }, [executionId])

  return (
    <div className={styles['exec-stream-root']}>
      <h3 className={styles['exec-title']}>Live Agent Execution Stream</h3>

      {executionId ? (
        <div className={styles['timeline']}>
          {agents.length === 0 && !finalResponse && <div className={styles['empty-state']}>Waiting for agent events...</div>}

          {agents.map((step, i) => (
            <div key={i} className={styles['timeline-node']}>
              <div className={styles['timeline-dot']}>
                <AgentBadge status={step.status} />
              </div>
              <div className={styles['timeline-content']}>
                <div className={styles['agent-name']}>
                  {step.name}
                  <span className={styles['agent-time']}>{new Date(step.time).toLocaleTimeString()}</span>
                </div>
                <details className={styles['context-card']}>
                  <summary>▶ Events</summary>
                  <div>
                    {step.messages.map((m, idx) => (
                      <div key={idx} style={{ padding: '6px 0', color: '#475569' }}>{m.text}</div>
                    ))}
                  </div>
                </details>
              </div>
            </div>
          ))}

        </div>
      ) : (
        <div className={styles['empty-state']}>No active execution. Start a query to see live agent activity.</div>
      )}
    </div>
  )
}
