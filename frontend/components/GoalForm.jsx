// GoalForm component: collects a goal and posts to backend API
import { useState } from 'react'

export default function GoalForm({ onResult }) {
  const [title, setTitle] = useState('')
  const [desc, setDesc] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/api/goal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'local-user', title, description: desc }),
      })
      const data = await res.json()
      onResult?.(data)
    } catch (err) {
      onResult?.({ error: String(err) })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={submit} className="space-y-2">
      <div>
        <label className="block text-sm font-medium">Title</label>
        <input aria-label="Title" value={title} onChange={(e) => setTitle(e.target.value)} className="border p-2 w-full" />
      </div>
      <div>
        <label className="block text-sm font-medium">Description</label>
        <textarea aria-label="Description" value={desc} onChange={(e) => setDesc(e.target.value)} className="border p-2 w-full" />
      </div>
      <div className="flex items-center space-x-2">
        <button aria-label="submit" disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded">{loading ? 'Submitting...' : 'Submit'}</button>
        <button type="button" className="px-3 py-2 border rounded">Cancel</button>
        <div className="ml-auto"><a href="/workflow" className="text-sm underline">Open Workflow</a></div>
      </div>
    </form>
  )
}
