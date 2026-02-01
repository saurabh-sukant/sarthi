import React, { useState } from 'react'
import { submitFeedback } from '../services/api'
import styles from './Feedback.module.css'

export default function Feedback() {
  const [executionId, setExecutionId] = useState('')
  const [rating, setRating] = useState('up')
  const [comment, setComment] = useState('')
  const [loading, setLoading] = useState(false)

  async function send(e) {
    e.preventDefault()
    setLoading(true)
    try {
      await submitFeedback(executionId, rating, comment)
      alert('Thank you for your feedback')
      setExecutionId('')
      setComment('')
      setRating('up')
    } catch (err) {
      alert('Failed to submit feedback')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles['feedback-root']}>
      <div className={styles['content-section']}>
        <div className={styles['section-header']}>
          <h2>Knowledge Base</h2>
          <p>Provide feedback on resolutions and improve system learning</p>
        </div>

        <div className={styles['card']}>
          <h3>Submit Resolution Feedback</h3>
          <p className={styles['description']}>Help us improve by rating solutions and providing constructive feedback.</p>
          
          <form onSubmit={send} className={styles['form']}>
            <div className={styles['form-group']}>
              <label htmlFor="execution-id">Execution ID</label>
              <input
                id="execution-id"
                type="text"
                value={executionId}
                onChange={(e) => setExecutionId(e.target.value)}
                className={styles['input']}
                placeholder="e.g., 79c1e316-46f9-4f49-9f0f-232a53b2846c"
                required
              />
            </div>

            <div className={styles['form-group']}>
              <label htmlFor="rating">Resolution Quality</label>
              <select
                id="rating"
                value={rating}
                onChange={(e) => setRating(e.target.value)}
                className={styles['input']}
              >
                <option value="up">✓ Helpful</option>
                <option value="down">✗ Not Helpful</option>
              </select>
            </div>

            <div className={styles['form-group']}>
              <label htmlFor="comment">Comments</label>
              <textarea
                id="comment"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className={styles['input']}
                placeholder="Share your feedback to help us improve..."
                rows={5}
              />
            </div>

            <button type="submit" className={styles['button']} disabled={loading}>
              {loading ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
