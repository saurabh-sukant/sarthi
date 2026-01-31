import React, { useEffect, useState } from 'react'
import { listAgents, runIngestion, runSelfService } from '../services/api'

export default function Agents() {
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(false)

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
    const form = e.target
    const source_type = form.source_type.value
    const value = form.value.value
    const metadata = form.metadata.value ? JSON.parse(form.metadata.value) : {}
    try {
      await runIngestion(source_type, value, metadata)
      alert('Ingested')
      form.reset()
    } catch (err) {
      alert('Failed to ingest')
    }
  }

  async function runSelf(e) {
    e.preventDefault()
    const q = e.target.q.value
    try {
      await runSelfService(q)
      alert('Started self-service')
      e.target.reset()
    } catch (err) {
      alert('Failed')
    }
  }

  return (
    <div>
      <h3>Available Agents</h3>
      {loading ? <div>Loading...</div> : (
        <ul>
          {agents.map(a => <li key={a.name}>{a.name}</li>)}
        </ul>
      )}

      <h4>Ingest Document</h4>
      <form onSubmit={ingest}>
        <div>
          <label>Type</label>
          <select name="source_type">
            <option value="text">text</option>
            <option value="url">url</option>
          </select>
        </div>
        <div>
          <label>Value</label>
          <input name="value" />
        </div>
        <div>
          <label>Metadata (JSON)</label>
          <textarea name="metadata" />
        </div>
        <button>Ingest</button>
      </form>

      <h4>Self Service</h4>
      <form onSubmit={runSelf}>
        <input name="q" />
        <button>Run</button>
      </form>
    </div>
  )
}
