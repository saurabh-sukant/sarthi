import React, { useEffect, useState } from 'react'
import { listAgents, runIngestion, runSelfService } from '../services/api'
import styles from './Agents.module.css'

export default function Agents() {
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(false)
  const [ingestLoading, setIngestLoading] = useState(false)

  useEffect(() => {
    (async () => {
      setLoading(true)
      try {
        const res = await listAgents()
        setAgents(res || [])
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  async function ingest(e) {
    e.preventDefault()
    setIngestLoading(true)
    const form = e.target
    const source_type = form.source_type.value
    const value = form.value.value
    const metadata = form.metadata.value ? JSON.parse(form.metadata.value) : {}
    try {
      await runIngestion(source_type, value, metadata)
      alert('Document ingested successfully')
      form.reset()
    } catch (err) {
      alert('Failed to ingest document')
    } finally {
      setIngestLoading(false)
    }
  }

  async function runSelf(e) {
    e.preventDefault()
    setIngestLoading(true)
    const q = e.target.q.value
    try {
      await runSelfService(q)
      alert('Self-service query started')
      e.target.reset()
    } catch (err) {
      alert('Failed to start self-service')
    } finally {
      setIngestLoading(false)
    }
  }

  return (
    <div className={styles['agents-root']}>
      <div className={styles['content-section']}>
        <div className={styles['section-header']}>
          <h2>Memory Bank</h2>
          <p>Manage stored memories and knowledge base ingestion</p>
        </div>

        <div className={styles['card']}>
          <h3>Available Agents</h3>
          {loading ? (
            <div className={styles['loading']}>Loading agents...</div>
          ) : agents.length === 0 ? (
            <div className={styles['empty-state']}>No agents available</div>
          ) : (
            <ul className={styles['agent-list']}>
              {agents.map(a => (
                <li key={a.name} className={styles['agent-item']}>
                  <span className={styles['agent-badge']}>⚙</span>
                  <span>{a.name}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className={styles['card']}>
          <h3>Ingest Document</h3>
          <form onSubmit={ingest} className={styles['form']}>
            <div className={styles['form-group']}>
              <label htmlFor="source_type">Source Type</label>
              <select id="source_type" name="source_type" className={styles['input']} required>
                <option value="text">Text</option>
                <option value="url">URL</option>
              </select>
            </div>
            <div className={styles['form-group']}>
              <label htmlFor="value">Value</label>
              <input id="value" name="value" className={styles['input']} placeholder="Enter text or URL" required />
            </div>
            <div className={styles['form-group']}>
              <label htmlFor="metadata">Metadata (JSON)</label>
              <textarea id="metadata" name="metadata" className={styles['input']} placeholder='{"key": "value"}' />
            </div>
            <button type="submit" className={styles['button']} disabled={ingestLoading}>
              {ingestLoading ? 'Ingesting...' : 'Ingest Document'}
            </button>
          </form>
        </div>

        <div className={styles['card']}>
          <h3>Self-Service Query</h3>
          <form onSubmit={runSelf} className={styles['form']}>
            <div className={styles['form-group']}>
              <label htmlFor="query">Query</label>
              <input id="query" name="q" className={styles['input']} placeholder="Enter your query" required />
            </div>
            <button type="submit" className={styles['button']} disabled={ingestLoading}>
              {ingestLoading ? 'Running...' : 'Run Query'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
