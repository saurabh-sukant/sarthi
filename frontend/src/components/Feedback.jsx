import React, { useState } from 'react'
import { submitFeedback } from '../services/api'

export default function Feedback() {
  const [executionId, setExecutionId] = useState('')
  const [rating, setRating] = useState('up')
  const [comment, setComment] = useState('')

  async function send(e) {
    e.preventDefault()
    try {
      await submitFeedback(executionId, rating, comment)
      alert('Thanks for the feedback')
      setExecutionId('')
      setComment('')
    } catch (err) {
      alert('Failed to submit feedback')
    }
  }

  return (
    <form onSubmit={send}>
      <div>
        <label>Execution ID</label>
        <input value={executionId} onChange={(e) => setExecutionId(e.target.value)} />
      </div>
      <div>
        <label>Rating</label>
        <select value={rating} onChange={(e) => setRating(e.target.value)}>
          <option value="up">Up</option>
          <option value="down">Down</option>
        </select>
      </div>
      <div>
        <label>Comment</label>
        <textarea value={comment} onChange={(e) => setComment(e.target.value)} />
      </div>
      <button>Submit Feedback</button>
    </form>
  )
}
