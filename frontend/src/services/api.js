import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

client.interceptors.response.use(
  (res) => res,
  (err) => {
    return Promise.reject(err)
  }
)

export async function submitChatQuery(query, attachments = [], mode = 'chat') {
  const res = await client.post('/chat/query', { query, attachments, mode })
  return res.data
}

export async function listAgents() {
  const res = await client.get('/agents')
  return res.data
}

export async function runSelfService(query) {
  const res = await client.post('/agents/self-service/run', { query })
  return res.data
}

export async function runIngestion(source_type, value, metadata = {}) {
  const res = await client.post('/agents/ingestion', { source_type, value, metadata })
  return res.data
}

export async function validateInput(content) {
  const res = await client.post('/guardrail/input', { content })
  return res.data
}

export async function validateOutput(content) {
  const res = await client.post('/guardrail/output', { content })
  return res.data
}

export async function listMemory() {
  const res = await client.get('/memory')
  return res.data
}

export async function updateMemory(id, content) {
  const res = await client.put(`/memory/${id}`, { content })
  return res.data
}

export async function deleteMemory(id) {
  const res = await client.delete(`/memory/${id}`)
  return res.data
}

export async function submitFeedback(execution_id, rating, comment) {
  const res = await client.post('/feedback', { execution_id, rating, comment })
  return res.data
}

export async function getDashboard(execution_id) {
  const res = await client.get(`/observability/dashboard/${execution_id}`)
  return res.data
}

export function createEventSource(execution_id) {
  const base = API_BASE.replace(/\/$/, '')
  return new EventSource(`${base}/api/chat/stream/${execution_id}`)
}
