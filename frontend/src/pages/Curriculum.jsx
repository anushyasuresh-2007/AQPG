import { useEffect, useState } from 'react'
import api from '../api'

const Curriculum = () => {
  const [statusData, setStatusData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [syncingBoard, setSyncingBoard] = useState(null)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('info')

  // Catalog Explorer States
  const [boards, setBoards] = useState([])
  const [selectedBoardId, setSelectedBoardId] = useState('')
  const [classes, setClasses] = useState([])
  const [selectedClassId, setSelectedClassId] = useState('')
  const [subjects, setSubjects] = useState([])
  const [selectedSubjectId, setSelectedSubjectId] = useState('')
  const [units, setUnits] = useState([])
  const [loadingCatalog, setLoadingCatalog] = useState(false)

  const loadStatus = async () => {
    setLoading(true)
    try {
      const res = await api.get('/curriculum/status')
      setStatusData(res.data)
      setBoards(res.data.boards || [])
      if (res.data.boards && res.data.boards.length > 0 && !selectedBoardId) {
        setSelectedBoardId(String(res.data.boards[0].id))
      }
    } catch (err) {
      setMessage('Failed to load curriculum sync status.')
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStatus()
  }, [])

  // When Board changes in explorer
  useEffect(() => {
    if (!selectedBoardId) return
    const fetchClasses = async () => {
      try {
        const res = await api.get(`/classes?board_id=${selectedBoardId}`)
        setClasses(res.data)
        if (res.data.length > 0) {
          setSelectedClassId(String(res.data[0].id))
        } else {
          setSelectedClassId('')
          setSubjects([])
          setUnits([])
        }
      } catch (err) {
        // Handled
      }
    }
    fetchClasses()
  }, [selectedBoardId])

  // When Class changes in explorer
  useEffect(() => {
    if (!selectedBoardId || !selectedClassId) return
    const fetchSubjects = async () => {
      setLoadingCatalog(true)
      try {
        const res = await api.get(`/subjects?board_id=${selectedBoardId}&class_id=${selectedClassId}`)
        setSubjects(res.data)
        if (res.data.length > 0) {
          setSelectedSubjectId(String(res.data[0].id))
        } else {
          setSelectedSubjectId('')
          setUnits([])
        }
      } catch (err) {
        // Handled
      } finally {
        setLoadingCatalog(false)
      }
    }
    fetchSubjects()
  }, [selectedBoardId, selectedClassId])

  // When Subject changes in explorer
  useEffect(() => {
    if (!selectedSubjectId) return
    const fetchUnits = async () => {
      try {
        const res = await api.get(`/units?subject_id=${selectedSubjectId}`)
        setUnits(res.data)
      } catch (err) {
        // Handled
      }
    }
    fetchUnits()
  }, [selectedSubjectId])

  const handleSync = async (boardKey) => {
    setSyncingBoard(boardKey)
    setMessage('')
    try {
      const res = await api.post('/curriculum/sync', {
        board: boardKey,
        academic_year: '2026-27',
      })
      setMessage(`Successfully synchronized ${res.data.board_code} (${res.data.academic_year}) official curriculum: ${res.data.subjects_count} subjects, ${res.data.units_count} syllabus units.`)
      setMessageType('success')
      await loadStatus()
    } catch (err) {
      setMessage(err?.response?.data?.detail || 'Curriculum synchronization failed.')
      setMessageType('error')
    } finally {
      setSyncingBoard(null)
    }
  }

  const selectedBoard = boards.find((b) => b.id === Number(selectedBoardId))
  const selectedClass = classes.find((c) => c.id === Number(selectedClassId))
  const selectedSubject = subjects.find((s) => s.id === Number(selectedSubjectId))

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-4 md:p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 dark:text-white flex items-center gap-3">
            <span>🌐</span> Official Curriculum Management
          </h1>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
            Authoritative curriculum catalog and synchronization engine for CBSE, Tamil Nadu State Board, and extensible regional boards.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => handleSync('cbse')}
            disabled={syncingBoard !== null}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition shadow-sm flex items-center gap-2"
          >
            {syncingBoard === 'cbse' ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Syncing CBSE...</span>
              </>
            ) : (
              <>
                <span>⚡</span>
                <span>Sync CBSE 2026-27</span>
              </>
            )}
          </button>

          <button
            onClick={() => handleSync('tnsb')}
            disabled={syncingBoard !== null}
            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition shadow-sm flex items-center gap-2"
          >
            {syncingBoard === 'tnsb' ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Syncing TNSB...</span>
              </>
            ) : (
              <>
                <span>⚡</span>
                <span>Sync Tamil Nadu 2026-27</span>
              </>
            )}
          </button>

          <button
            onClick={loadStatus}
            disabled={loading}
            className="px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-200 text-xs font-bold transition"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Message notification */}
      {message && (
        <div
          className={`p-4 rounded-xl text-sm font-medium border flex items-center gap-3 ${
            messageType === 'error'
              ? 'bg-rose-50 border-rose-200 text-rose-800 dark:bg-rose-950/40 dark:border-rose-800 dark:text-rose-300'
              : 'bg-emerald-50 border-emerald-200 text-emerald-800 dark:bg-emerald-950/40 dark:border-emerald-800 dark:text-emerald-300'
          }`}
        >
          <span>{messageType === 'error' ? '⚠️' : '✅'}</span>
          <span>{message}</span>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-slate-800 p-5 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-1">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Educational Boards</span>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            {statusData?.boards?.length || 0} Supported
          </div>
          <p className="text-xs text-slate-500">CBSE & Tamil Nadu State Board</p>
        </div>

        <div className="bg-white dark:bg-slate-800 p-5 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-1">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Curriculum Subjects</span>
          <div className="text-2xl font-black text-indigo-600 dark:text-indigo-400">
            {statusData?.total_subjects || 0} Registered
          </div>
          <p className="text-xs text-slate-500">Secondary & Senior Secondary</p>
        </div>

        <div className="bg-white dark:bg-slate-800 p-5 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-1">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Official Syllabus Units</span>
          <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
            {statusData?.total_units || 0} Units
          </div>
          <p className="text-xs text-slate-500">Structured syllabus decompositions</p>
        </div>
      </div>

      {/* Interactive Curriculum Catalog Explorer */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-700 pb-4">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <span>📚</span> Interactive Curriculum Explorer
          </h2>
          <span className="text-xs text-slate-500 dark:text-slate-400">
            Browse official subjects and syllabus units by Board & Class
          </span>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Educational Board
            </label>
            <select
              className="w-full rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={selectedBoardId}
              onChange={(e) => setSelectedBoardId(e.target.value)}
            >
              {boards.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name} ({b.code})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Academic Class
            </label>
            <select
              className="w-full rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={selectedClassId}
              onChange={(e) => setSelectedClassId(e.target.value)}
              disabled={classes.length === 0}
            >
              {classes.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.class_code}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Syllabus Subject
            </label>
            <select
              className="w-full rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={selectedSubjectId}
              onChange={(e) => setSelectedSubjectId(e.target.value)}
              disabled={subjects.length === 0}
            >
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.subject_name} {s.subject_code ? `(${s.subject_code})` : ''}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Selected Subject & Units Details */}
        {selectedSubject ? (
          <div className="bg-slate-50 dark:bg-slate-900/60 rounded-xl p-5 border border-slate-200 dark:border-slate-700 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <span>📖</span> {selectedSubject.subject_name}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {selectedBoard?.code} · {selectedClass?.class_code} · Code: {selectedSubject.subject_code || 'N/A'}
                </p>
              </div>
              {selectedSubject.source_url && (
                <a
                  href={selectedSubject.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                >
                  <span>🔗</span> Official Syllabus Source
                </a>
              )}
            </div>

            <div>
              <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-3">
                Official Curriculum Units ({units.length})
              </h4>
              {units.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No units registered for this subject.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                  {units.map((u, idx) => (
                    <div
                      key={u.id}
                      className="flex items-center gap-3 p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-800 dark:text-slate-200"
                    >
                      <span className="flex items-center justify-center w-5 h-5 rounded-md bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-bold text-[10px]">
                        {idx + 1}
                      </span>
                      <span className="flex-1">{u.unit_name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-sm text-slate-400">
            Select a board, class, and subject above to inspect curriculum units.
          </div>
        )}
      </div>

      {/* Structured Syllabus Ingestion Tool */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <span>📥</span> Ingest Structured Syllabus Dataset (JSON / YAML)
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Import complete Board, Class, Subject, Unit, and Topic hierarchies directly into the AQPG catalog.
            </p>
          </div>
        </div>

        <form
          onSubmit={async (e) => {
            e.preventDefault();
            const textarea = e.target.elements.syllabus_json;
            try {
              setMessage("Ingesting structured syllabus dataset...");
              setMessageType("info");
              const parsed = JSON.parse(textarea.value);
              const res = await api.post("/syllabus/import", parsed);
              setMessage(res.data?.message || "Syllabus dataset successfully ingested!");
              setMessageType("success");
              loadStatus();
            } catch (err) {
              setMessage(err.response?.data?.detail || "Invalid JSON or ingestion error: " + err.message);
              setMessageType("error");
            }
          }}
          className="space-y-3"
        >
          <textarea
            name="syllabus_json"
            rows="5"
            placeholder={`[\n  {\n    "board": "CBSE",\n    "class": 10,\n    "subjects": [\n      {\n        "name": "Mathematics",\n        "code": "041",\n        "units": [\n          { "name": "Real Numbers", "topics": ["Euclid Division", "Fundamental Theorem"] }\n        ]\n      }\n    ]\n  }\n]`}
            className="w-full font-mono text-xs p-3 bg-slate-900 text-slate-200 rounded-xl border border-slate-700 focus:outline-none focus:border-indigo-500"
            defaultValue={`[
  {
    "board": "CBSE",
    "class": 10,
    "subjects": [
      {
        "name": "Mathematics",
        "code": "041",
        "units": [
          {
            "name": "Real Numbers",
            "topics": ["Euclid's Division Lemma", "Fundamental Theorem of Arithmetic"]
          }
        ]
      }
    ]
  }
]`}
          ></textarea>
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-400">
              Valid JSON schema with <code>board</code>, <code>class</code>, <code>subjects</code>, <code>units</code>, and <code>topics</code>.
            </span>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition shadow-sm"
            >
              📥 Ingest Syllabus JSON
            </button>
          </div>
        </form>
      </div>

      {/* Sync Logs Table */}
      {statusData?.sync_logs && statusData.sync_logs.length > 0 && (
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm space-y-4">
          <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <span>📋</span> Curriculum Synchronization Audit History
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-300 font-semibold">
                  <th className="py-2.5 px-3">Board</th>
                  <th className="py-2.5 px-3">Academic Session</th>
                  <th className="py-2.5 px-3">Classes Synced</th>
                  <th className="py-2.5 px-3 text-center">Subjects</th>
                  <th className="py-2.5 px-3 text-center">Units</th>
                  <th className="py-2.5 px-3 text-center">Status</th>
                  <th className="py-2.5 px-3">Synced At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
                {statusData.sync_logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                    <td className="py-2 px-3 font-bold text-slate-900 dark:text-white">{log.board_code}</td>
                    <td className="py-2 px-3 font-semibold">{log.academic_year}</td>
                    <td className="py-2 px-3 text-slate-500">{log.classes_synced}</td>
                    <td className="py-2 px-3 text-center font-bold text-indigo-600 dark:text-indigo-400">{log.subjects_count}</td>
                    <td className="py-2 px-3 text-center font-bold text-emerald-600 dark:text-emerald-400">{log.units_count}</td>
                    <td className="py-2 px-3 text-center">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 uppercase">
                        {log.status}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-slate-400">{new Date(log.synced_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default Curriculum

