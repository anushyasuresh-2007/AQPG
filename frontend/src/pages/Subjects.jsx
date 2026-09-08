import { useEffect, useState } from 'react'
import api from '../api'

const Subjects = () => {
  const [subjects, setSubjects] = useState([])
  const [subjectName, setSubjectName] = useState('')
  const [className, setClassName] = useState('12')
  const [board, setBoard] = useState('CBSE')
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  
  // Edit State
  const [editingSubject, setEditingSubject] = useState(null)
  const [editForm, setEditForm] = useState({ subject_name: '', class_name: '', board: '' })

  const loadSubjects = async () => {
    setLoading(true)
    try {
      const response = await api.get('/subjects')
      setSubjects(response.data)
      setMessage('')
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Unable to load subjects')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadSubjects() }, [])

  const addSubject = async (e) => {
    e.preventDefault()
    try {
      await api.post('/subjects', { subject_name: subjectName, class_name: className, board })
      setSubjectName('')
      setClassName('12')
      setBoard('CBSE')
      setMessage('Subject added')
      loadSubjects()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Unable to add subject')
    }
  }

  const deleteSubject = async (id) => {
    if (!window.confirm('Are you sure you want to delete this subject? This will delete all units and questions under it.')) return
    try {
      await api.delete(`/subjects/${id}`)
      setMessage('Subject deleted')
      loadSubjects()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Unable to delete subject')
    }
  }

  const startEdit = (subject) => {
    setEditingSubject(subject.id)
    setEditForm({
      subject_name: subject.subject_name,
      class_name: subject.class_name,
      board: subject.board
    })
  }

  const cancelEdit = () => {
    setEditingSubject(null)
  }

  const saveEdit = async (id) => {
    try {
      await api.put(`/subjects/${id}`, editForm)
      setEditingSubject(null)
      setMessage('Subject updated')
      loadSubjects()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Unable to update subject')
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 p-6">
      <div className="mx-auto max-w-5xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold">Subjects</h1>
        <p className="mb-4 text-slate-600">Create and review subjects for the question bank.</p>
        <form onSubmit={addSubject} className="mb-6 flex gap-3">
          <input className="flex-1 rounded-lg border px-3 py-2" placeholder="Subject name" value={subjectName} onChange={(e) => setSubjectName(e.target.value)} />
          <input className="w-24 rounded-lg border px-3 py-2" placeholder="Class" value={className} onChange={(e) => setClassName(e.target.value)} />
          <input className="w-32 rounded-lg border px-3 py-2" placeholder="Board" value={board} onChange={(e) => setBoard(e.target.value)} />
          <button className="rounded-lg bg-slate-900 px-4 py-2 text-white">Add</button>
        </form>
        {message ? <p className="mb-4 text-sm text-slate-700">{message}</p> : null}
        {loading ? <p>Loading...</p> : (
          <div className="grid gap-3">
            {subjects.map((subject) => (
              <div key={subject.id} className="flex items-center justify-between rounded-lg border p-3 bg-white hover:bg-slate-50 transition">
                {editingSubject === subject.id ? (
                  <div className="flex flex-1 gap-2">
                    <input className="flex-1 rounded-md border px-2 py-1 text-sm" value={editForm.subject_name} onChange={(e) => setEditForm({ ...editForm, subject_name: e.target.value })} />
                    <input className="w-16 rounded-md border px-2 py-1 text-sm" value={editForm.class_name} onChange={(e) => setEditForm({ ...editForm, class_name: e.target.value })} />
                    <input className="w-24 rounded-md border px-2 py-1 text-sm" value={editForm.board} onChange={(e) => setEditForm({ ...editForm, board: e.target.value })} />
                    <button onClick={() => saveEdit(subject.id)} className="rounded bg-green-600 px-3 py-1 text-xs text-white hover:bg-green-700">Save</button>
                    <button onClick={cancelEdit} className="rounded bg-slate-400 px-3 py-1 text-xs text-white hover:bg-slate-500">Cancel</button>
                  </div>
                ) : (
                  <>
                    <div className="font-medium">
                      {subject.subject_name || <span className="italic text-slate-400">Untitled Subject</span>} · Class {subject.class_name} · {subject.board}
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => startEdit(subject)} className="rounded border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50">Edit</button>
                      <button onClick={() => deleteSubject(subject.id)} className="rounded bg-red-600 px-3 py-1 text-xs font-medium text-white hover:bg-red-700">Delete</button>
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

export default Subjects
