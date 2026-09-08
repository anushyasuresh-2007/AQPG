import { useEffect, useState } from 'react'
import api from '../api'

const Units = () => {
  const [units, setUnits] = useState([])
  const [unitName, setUnitName] = useState('')
  const [subjectId, setSubjectId] = useState('')
  const [subjects, setSubjects] = useState([])
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)

  // Edit State
  const [editingUnit, setEditingUnit] = useState(null)
  const [editForm, setEditForm] = useState({ unit_name: '', subject_id: '' })

  // AI Importer State
  const [fetchingSyllabus, setFetchingSyllabus] = useState(false)
  const [fetchedUnits, setFetchedUnits] = useState([]) // holds { name, selected }

  const loadData = async () => {
    setLoading(true)
    try {
      const [unitResponse, subjectResponse] = await Promise.all([api.get('/units'), api.get('/subjects')])
      setUnits(unitResponse.data)
      setSubjects(subjectResponse.data)
      setMessage('')
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Unable to load units')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData() }, [])

  const addUnit = async (e) => {
    e.preventDefault()
    try {
      await api.post('/units', { unit_name: unitName, subject_id: Number(subjectId) })
      setUnitName('')
      setSubjectId('')
      setMessage('Unit added')
      loadData()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Unable to add unit')
    }
  }

  const deleteUnit = async (id) => {
    if (!window.confirm('Are you sure you want to delete this unit? This will delete all questions under it.')) return
    try {
      await api.delete(`/units/${id}`)
      setMessage('Unit deleted')
      loadData()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Unable to delete unit')
    }
  }

  const startEdit = (unit) => {
    setEditingUnit(unit.id)
    setEditForm({
      unit_name: unit.unit_name,
      subject_id: String(unit.subject_id)
    })
  }

  const cancelEdit = () => {
    setEditingUnit(null)
  }

  const saveEdit = async (id) => {
    try {
      await api.put(`/units/${id}`, {
        unit_name: editForm.unit_name,
        subject_id: Number(editForm.subject_id)
      })
      setEditingUnit(null)
      setMessage('Unit updated')
      loadData()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Unable to update unit')
    }
  }

  // AI Syllabus Fetcher Handlers
  const handleFetchSyllabus = async () => {
    if (!subjectId) {
      setMessage('Please select a subject to fetch syllabus for first.')
      return
    }
    setFetchingSyllabus(true)
    setMessage('')
    setFetchedUnits([])
    try {
      const response = await api.post('/units/fetch-syllabus', {
        subject_id: Number(subjectId)
      })
      const items = (response.data.units || []).map((name) => ({
        name,
        selected: true
      }))
      setFetchedUnits(items)
      if (items.length === 0) {
        setMessage('No chapters found for this syllabus.')
      } else {
        setMessage(`Found ${items.length} chapters! Review and import below.`)
      }
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Failed to fetch syllabus chapters.')
    } finally {
      setFetchingSyllabus(false)
    }
  }

  const handleImportSyllabus = async () => {
    const toImport = fetchedUnits.filter(u => u.selected && u.name.trim())
    if (toImport.length === 0) {
      setMessage('Select at least one chapter to import.')
      return
    }
    setLoading(true)
    let count = 0
    try {
      for (const item of toImport) {
        await api.post('/units', {
          unit_name: item.name,
          subject_id: Number(subjectId)
        })
        count++
      }
      setMessage(`Successfully imported ${count} chapter(s) to this subject syllabus.`)
      setFetchedUnits([])
      loadData()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Error importing syllabus chapters.')
    } finally {
      setLoading(false)
    }
  }

  const getSubjectName = (subId) => {
    const found = subjects.find(s => s.id === subId)
    return found ? `${found.subject_name} (Class ${found.class_name} · ${found.board})` : `Subject #${subId}`
  }

  return (
    <div className="min-h-screen bg-slate-100 p-6">
      <div className="mx-auto max-w-5xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold">Syllabus Chapters & Units</h1>
        <p className="mb-4 text-slate-600">Populate exam units manually or automatically from NCERT / State Boards.</p>
        
        {/* Main Syllabus Form */}
        <form onSubmit={addUnit} className="mb-6 space-y-3 bg-slate-50 p-4 rounded-xl border">
          <h2 className="text-sm font-semibold text-slate-700">Add Units / Chapters</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <select className="rounded-lg border px-3 py-2 bg-white text-sm" value={subjectId} onChange={(e) => setSubjectId(e.target.value)}>
              <option value="">Select subject</option>
              {subjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.subject_name} (Class {subject.class_name} · {subject.board})</option>)}
            </select>
            <div className="flex gap-2">
              <input className="flex-1 rounded-lg border px-3 py-2 bg-white text-sm" placeholder="Manual chapter name" value={unitName} onChange={(e) => setUnitName(e.target.value)} />
              <button className="rounded-lg bg-slate-900 px-4 py-2 text-white text-xs font-semibold hover:bg-slate-800 transition">Add</button>
            </div>
          </div>
          
          <div className="pt-2 border-t flex flex-wrap gap-2">
            <button
              type="button"
              disabled={fetchingSyllabus || !subjectId}
              onClick={handleFetchSyllabus}
              className="rounded-lg bg-indigo-600 hover:bg-indigo-700 px-4 py-2 text-xs font-semibold text-white transition disabled:opacity-50"
            >
              {fetchingSyllabus ? 'Fetching NCERT/Stateboard Chapters...' : '🤖 AI Fetch Standard Syllabus Chapters'}
            </button>
          </div>

          {/* AI Syllabus Importer checklist */}
          {fetchedUnits.length > 0 && (
            <div className="mt-4 pt-4 border-t space-y-3 bg-white p-3 rounded-lg border">
              <h3 className="text-xs font-bold text-slate-700">Select standard board chapters to import:</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-48 overflow-y-auto p-1">
                {fetchedUnits.map((item, idx) => (
                  <label key={idx} className="flex gap-2 items-center text-xs text-slate-700 hover:bg-slate-50 p-1.5 rounded cursor-pointer border font-sans">
                    <input
                      type="checkbox"
                      checked={item.selected}
                      onChange={() => {
                        const next = [...fetchedUnits]
                        next[idx].selected = !next[idx].selected
                        setFetchedUnits(next)
                      }}
                    />
                    <span>{item.name}</span>
                  </label>
                ))}
              </div>
              <button
                type="button"
                onClick={handleImportSyllabus}
                className="rounded-lg bg-green-600 hover:bg-green-700 px-4 py-2 text-xs font-semibold text-white transition"
              >
                Import Checked Chapters to Syllabus
              </button>
            </div>
          )}
        </form>

        {message ? <p className="mb-6 text-sm text-slate-700 font-medium bg-slate-50 border p-3 rounded-lg">{message}</p> : null}
        
        {loading ? <p>Loading syllabus index...</p> : (
          <div className="grid gap-3">
            {units.map((unit) => (
              <div key={unit.id} className="flex items-center justify-between rounded-lg border p-3 bg-white hover:bg-slate-50 transition">
                {editingUnit === unit.id ? (
                  <div className="flex flex-1 gap-2">
                    <input className="flex-1 rounded-md border px-2 py-1 text-sm" value={editForm.unit_name} onChange={(e) => setEditForm({ ...editForm, unit_name: e.target.value })} />
                    <select className="w-48 rounded-md border px-2 py-1 text-sm" value={editForm.subject_id} onChange={(e) => setEditForm({ ...editForm, subject_id: e.target.value })}>
                      {subjects.map((sub) => <option key={sub.id} value={sub.id}>{sub.subject_name}</option>)}
                    </select>
                    <button onClick={() => saveEdit(unit.id)} className="rounded bg-green-600 px-3 py-1 text-xs text-white hover:bg-green-700">Save</button>
                    <button onClick={cancelEdit} className="rounded bg-slate-400 px-3 py-1 text-xs text-white hover:bg-slate-500">Cancel</button>
                  </div>
                ) : (
                  <>
                    <div className="font-medium text-slate-800">
                      {unit.unit_name || <span className="italic text-slate-400">Untitled Unit</span>}
                      <span className="ml-2 text-[10px] font-normal text-slate-500 bg-slate-100 rounded px-2 py-0.5 whitespace-nowrap font-sans">
                        {getSubjectName(unit.subject_id)}
                      </span>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => startEdit(unit)} className="rounded border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50">Edit</button>
                      <button onClick={() => deleteUnit(unit.id)} className="rounded bg-red-600 px-3 py-1 text-xs font-medium text-white hover:bg-red-700">Delete</button>
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

export default Units
