import { useEffect, useState } from 'react'
import api from '../api'

const BloomLevels = () => {
  const [blooms, setBlooms] = useState([])
  const [levelName, setLevelName] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)

  // Edit State
  const [editingBloom, setEditingBloom] = useState(null)
  const [editForm, setEditForm] = useState({ level_name: '' })

  const loadBlooms = async () => {
    setLoading(true)
    try {
      const response = await api.get('/bloom-levels')
      setBlooms(response.data)
      setMessage('')
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Unable to load Bloom levels')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadBlooms() }, [])

  const addBloom = async (e) => {
    e.preventDefault()
    try {
      await api.post('/bloom-levels', { level_name: levelName })
      setLevelName('')
      setMessage('Bloom level added')
      loadBlooms()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Unable to add Bloom level')
    }
  }

  const deleteBloom = async (id) => {
    if (!window.confirm('Are you sure you want to delete this Bloom level?')) return
    try {
      await api.delete(`/bloom-levels/${id}`)
      setMessage('Bloom level deleted')
      loadBlooms()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Unable to delete Bloom level')
    }
  }

  const startEdit = (bloom) => {
    setEditingBloom(bloom.id)
    setEditForm({ level_name: bloom.level_name })
  }

  const cancelEdit = () => {
    setEditingBloom(null)
  }

  const saveEdit = async (id) => {
    try {
      await api.put(`/bloom-levels/${id}`, editForm)
      setEditingBloom(null)
      setMessage('Bloom level updated')
      loadBlooms()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Unable to update Bloom level')
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 p-6">
      <div className="mx-auto max-w-5xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold">Bloom Levels</h1>
        <p className="mb-4 text-slate-600">Add learning levels for question distribution.</p>
        <form onSubmit={addBloom} className="mb-6 flex gap-3">
          <input className="flex-1 rounded-lg border px-3 py-2" placeholder="Bloom level" value={levelName} onChange={(e) => setLevelName(e.target.value)} />
          <button className="rounded-lg bg-slate-900 px-4 py-2 text-white">Add</button>
        </form>
        {message ? <p className="mb-4 text-sm text-slate-700">{message}</p> : null}
        {loading ? <p>Loading...</p> : (
          <div className="grid gap-3">
            {blooms.map((bloom) => (
              <div key={bloom.id} className="flex items-center justify-between rounded-lg border p-3 bg-white hover:bg-slate-50 transition">
                {editingBloom === bloom.id ? (
                  <div className="flex flex-1 gap-2">
                    <input className="flex-1 rounded-md border px-2 py-1 text-sm" value={editForm.level_name} onChange={(e) => setEditForm({ ...editForm, level_name: e.target.value })} />
                    <button onClick={() => saveEdit(bloom.id)} className="rounded bg-green-600 px-3 py-1 text-xs text-white hover:bg-green-700">Save</button>
                    <button onClick={cancelEdit} className="rounded bg-slate-400 px-3 py-1 text-xs text-white hover:bg-slate-500">Cancel</button>
                  </div>
                ) : (
                  <>
                    <div className="font-medium">
                      {bloom.level_name || <span className="italic text-slate-400">Unnamed Bloom Level</span>}
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => startEdit(bloom)} className="rounded border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50">Edit</button>
                      <button onClick={() => deleteBloom(bloom.id)} className="rounded bg-red-600 px-3 py-1 text-xs font-medium text-white hover:bg-red-700">Delete</button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default BloomLevels
