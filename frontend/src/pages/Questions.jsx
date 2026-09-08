import { useEffect, useMemo, useState } from 'react'
import api from '../api'

const Questions = () => {
  const [questions, setQuestions] = useState([])
  const [subjects, setSubjects] = useState([])
  const [units, setUnits] = useState([])
  const [blooms, setBlooms] = useState([])
  
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('info') // 'info' | 'error' | 'success'

  // Tab mode: 'list' | 'add' | 'bulk' | 'ai'
  const [activeTab, setActiveTab] = useState('list')

  // Search & Filters
  const [search, setSearch] = useState('')
  const [filterSubject, setFilterSubject] = useState('')
  const [filterUnit, setFilterUnit] = useState('')
  const [filterBloom, setFilterBloom] = useState('')
  const [filterDifficulty, setFilterDifficulty] = useState('')
  const [filterType, setFilterType] = useState('')
  const [filterMarks, setFilterMarks] = useState('')

  // Add Question Form
  const [form, setForm] = useState({
    subject_id: '',
    unit_id: '',
    bloom_level_id: '',
    question_text: '',
    question_type: 'Short Answer',
    marks: 5,
    difficulty: 'medium',
    answer: '',
    explanation: '',
  })

  // Edit Modal State
  const [editingQuestion, setEditingQuestion] = useState(null)
  const [editForm, setEditForm] = useState({
    id: null,
    subject_id: '',
    unit_id: '',
    bloom_level_id: '',
    question_text: '',
    question_type: 'Short Answer',
    marks: 5,
    difficulty: 'medium',
    answer: '',
    explanation: '',
  })

  // Bulk Upload State
  const [bulkCsvText, setBulkCsvText] = useState('')
  const [bulkUploading, setBulkUploading] = useState(false)
  const [bulkResult, setBulkResult] = useState(null)

  // AI Drafter State
  const [aiForm, setAiForm] = useState({
    subject_id: '',
    unit_id: '',
    bloom_level_id: '',
    difficulty: 'medium',
    marks: 5,
    count: 3,
    textbook_context: '',
  })
  const [aiGenerating, setAiGenerating] = useState(false)
  const [aiQuestions, setAiQuestions] = useState([])

  const loadData = async () => {
    setLoading(true)
    try {
      const [questionRes, subjectRes, unitRes, bloomRes] = await Promise.all([
        api.get('/questions?limit=500'),
        api.get('/subjects'),
        api.get('/units'),
        api.get('/bloom-levels'),
      ])
      setQuestions(questionRes.data)
      setSubjects(subjectRes.data)
      setUnits(unitRes.data)
      setBlooms(bloomRes.data)

      // Set default subject/unit if available
      if (subjectRes.data.length > 0 && !form.subject_id) {
        const firstSub = subjectRes.data[0]
        setForm((prev) => ({ ...prev, subject_id: String(firstSub.id) }))
        setAiForm((prev) => ({ ...prev, subject_id: String(firstSub.id) }))
      }
      if (bloomRes.data.length > 0 && !form.bloom_level_id) {
        setForm((prev) => ({ ...prev, bloom_level_id: String(bloomRes.data[0].id) }))
        setAiForm((prev) => ({ ...prev, bloom_level_id: String(bloomRes.data[0].id) }))
      }
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Unable to load question bank data.')
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  // Filter units for the selected subject in add/filter forms
  const filteredUnitsForAdd = useMemo(() => {
    if (!form.subject_id) return units
    return units.filter((u) => u.subject_id === Number(form.subject_id))
  }, [units, form.subject_id])

  const filteredUnitsForFilter = useMemo(() => {
    if (!filterSubject) return units
    return units.filter((u) => u.subject_id === Number(filterSubject))
  }, [units, filterSubject])

  const filteredUnitsForAI = useMemo(() => {
    if (!aiForm.subject_id) return units
    return units.filter((u) => u.subject_id === Number(aiForm.subject_id))
  }, [units, aiForm.subject_id])

  // Filter questions list
  const visibleQuestions = useMemo(() => {
    return questions.filter((q) => {
      if (filterSubject && q.subject_id !== Number(filterSubject)) return false
      if (filterUnit && q.unit_id !== Number(filterUnit)) return false
      if (filterBloom && q.bloom_level_id !== Number(filterBloom)) return false
      if (filterDifficulty && q.difficulty?.toLowerCase() !== filterDifficulty.toLowerCase()) return false
      if (filterType && q.question_type !== filterType) return false
      if (filterMarks && q.marks !== Number(filterMarks)) return false
      if (search.trim()) {
        const query = search.toLowerCase()
        const matchText = q.question_text?.toLowerCase().includes(query)
        const matchAns = q.answer?.toLowerCase().includes(query)
        const matchExpl = q.explanation?.toLowerCase().includes(query)
        if (!matchText && !matchAns && !matchExpl) return false
      }
      return true
    })
  }, [questions, filterSubject, filterUnit, filterBloom, filterDifficulty, filterType, filterMarks, search])

  // Add Question
  const handleAddQuestion = async (e) => {
    e.preventDefault()
    if (!form.question_text.trim()) {
      setMessage('Question text is required.')
      setMessageType('error')
      return
    }
    if (!form.subject_id || !form.unit_id || !form.bloom_level_id) {
      setMessage('Please select Subject, Unit, and Bloom Level.')
      setMessageType('error')
      return
    }

    try {
      await api.post('/questions', {
        subject_id: Number(form.subject_id),
        unit_id: Number(form.unit_id),
        bloom_level_id: Number(form.bloom_level_id),
        question_text: form.question_text.trim(),
        question_type: form.question_type || 'Short Answer',
        marks: Number(form.marks),
        difficulty: form.difficulty,
        answer: form.answer?.trim() || null,
        explanation: form.explanation?.trim() || null,
      })
      setMessage('Question successfully added to Question Bank!')
      setMessageType('success')
      setForm((prev) => ({ ...prev, question_text: '', answer: '', explanation: '' }))
      setActiveTab('list')
      loadData()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Failed to add question.')
      setMessageType('error')
    }
  }

  // Delete Question
  const handleDeleteQuestion = async (id) => {
    if (!window.confirm('Are you sure you want to delete this question from the Question Bank?')) return
    try {
      await api.delete(`/questions/${id}`)
      setMessage('Question deleted successfully.')
      setMessageType('success')
      loadData()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Failed to delete question.')
      setMessageType('error')
    }
  }

  // Start Edit
  const handleStartEdit = (q) => {
    setEditingQuestion(q.id)
    setEditForm({
      id: q.id,
      subject_id: String(q.subject_id),
      unit_id: String(q.unit_id),
      bloom_level_id: String(q.bloom_level_id),
      question_text: q.question_text || '',
      question_type: q.question_type || 'Short Answer',
      marks: q.marks || 1,
      difficulty: q.difficulty || 'medium',
      answer: q.answer || '',
      explanation: q.explanation || '',
    })
  }

  // Save Edit
  const handleSaveEdit = async () => {
    try {
      await api.put(`/questions/${editForm.id}`, {
        subject_id: Number(editForm.subject_id),
        unit_id: Number(editForm.unit_id),
        bloom_level_id: Number(editForm.bloom_level_id),
        question_text: editForm.question_text.trim(),
        question_type: editForm.question_type,
        marks: Number(editForm.marks),
        difficulty: editForm.difficulty,
        answer: editForm.answer?.trim() || null,
        explanation: editForm.explanation?.trim() || null,
      })
      setMessage('Question updated successfully!')
      setMessageType('success')
      setEditingQuestion(null)
      loadData()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Failed to update question.')
      setMessageType('error')
    }
  }

  // Parse and Submit Bulk CSV / JSON
  const handleBulkUpload = async () => {
    if (!bulkCsvText.trim()) {
      setMessage('Please paste CSV text or JSON data.')
      setMessageType('error')
      return
    }

    setBulkUploading(true)
    setBulkResult(null)
    setMessage('')

    try {
      let items = []
      const trimmed = bulkCsvText.trim()

      if (trimmed.startsWith('[')) {
        // Parse JSON format
        items = JSON.parse(trimmed)
      } else {
        // Parse CSV format
        // Expected columns: subject, unit, question_text (or question), marks, difficulty, bloom_level, question_type, answer, explanation
        const lines = trimmed.split('\n').filter((l) => l.trim().length > 0)
        if (lines.length <= 1) {
          throw new Error('CSV must contain a header line and at least one data row.')
        }

        const headers = lines[0].split(',').map((h) => h.trim().toLowerCase().replace(/['"]/g, ''))
        
        for (let i = 1; i < lines.length; i++) {
          // Simple CSV parser supporting quotes
          const rowValues = []
          let insideQuote = false
          let currentVal = ''
          const rowStr = lines[i]

          for (let c = 0; c < rowStr.length; c++) {
            const char = rowStr[c]
            if (char === '"') {
              insideQuote = !insideQuote
            } else if (char === ',' && !insideQuote) {
              rowValues.push(currentVal.trim().replace(/^"|"$/g, ''))
              currentVal = ''
            } else {
              currentVal += char
            }
          }
          rowValues.push(currentVal.trim().replace(/^"|"$/g, ''))

          const item = {}
          headers.forEach((h, colIdx) => {
            const val = rowValues[colIdx] || ''
            if (h.includes('subject')) item.subject_name = val
            else if (h.includes('unit')) item.unit_name = val
            else if (h.includes('bloom')) item.bloom_level = val
            else if (h.includes('mark')) item.marks = Number(val) || 1
            else if (h.includes('diff')) item.difficulty = val
            else if (h.includes('type')) item.question_type = val
            else if (h.includes('ans')) item.answer = val
            else if (h.includes('expl')) item.explanation = val
            else if (h.includes('quest') || h === 'text') item.question_text = val
          })

          if (item.question_text) {
            items.push(item)
          }
        }
      }

      if (items.length === 0) {
        throw new Error('No valid question rows found in input.')
      }

      const res = await api.post('/questions/bulk-upload', items)
      setBulkResult(res.data)
      setMessage(`Bulk Import Complete: ${res.data.successful_count} created, ${res.data.failed_count} failed.`)
      setMessageType(res.data.failed_count === 0 ? 'success' : 'info')
      loadData()
    } catch (err) {
      setMessage(err?.response?.data?.detail || err.message || 'Bulk upload failed.')
      setMessageType('error')
    } finally {
      setBulkUploading(false)
    }
  }

  const sampleCsvTemplate = `subject,unit,bloom_level,difficulty,marks,question_type,question_text,answer
Data Structures,Unit 1 - Introduction to Data Structures,Remember,easy,1,Short Answer,"What is the time complexity of array indexing?","O(1)"
Data Structures,Unit 2 - Arrays and Linked Lists,Understand,medium,3,Short Answer,"Explain difference between singly and doubly linked lists.","Doubly has prev and next pointers."
Data Structures,Unit 3 - Stacks and Queues,Apply,medium,5,Long Answer,"Write algorithm to implement a stack using two queues.","Enqueue to q2, dequeue all q1 to q2, swap queues."`

  // AI Question Generation Handlers
  const handleAIGenerate = async (e) => {
    e.preventDefault()
    if (!aiForm.subject_id || !aiForm.unit_id || !aiForm.bloom_level_id) {
      setMessage('Please select Subject, Unit, and Bloom Level.')
      setMessageType('error')
      return
    }
    setAiGenerating(true)
    setMessage('')
    setAiQuestions([])

    try {
      const res = await api.post('/questions/generate-ai', {
        subject_id: Number(aiForm.subject_id),
        unit_id: Number(aiForm.unit_id),
        bloom_level_id: Number(aiForm.bloom_level_id),
        difficulty: aiForm.difficulty,
        marks: Number(aiForm.marks),
        count: Number(aiForm.count),
        textbook_context: aiForm.textbook_context || null,
      })

      const list = (res.data.questions || []).map((q) => ({
        ...q,
        selected: true,
      }))
      setAiQuestions(list)
      if (list.length === 0) {
        setMessage('No questions were generated by the AI.')
        setMessageType('error')
      } else {
        setMessage(`AI drafted ${list.length} questions. Select and save them to the Question Bank below.`)
        setMessageType('success')
      }
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'AI generation failed.')
      setMessageType('error')
    } finally {
      setAiGenerating(false)
    }
  }

  const handleSaveAIQuestions = async () => {
    const selected = aiQuestions.filter((q) => q.selected && q.question_text.trim())
    if (selected.length === 0) {
      setMessage('Please select at least one question to save.')
      setMessageType('error')
      return
    }

    setLoading(true)
    let saved = 0
    try {
      for (const item of selected) {
        await api.post('/questions', {
          subject_id: Number(aiForm.subject_id),
          unit_id: Number(aiForm.unit_id),
          bloom_level_id: Number(aiForm.bloom_level_id),
          question_text: item.question_text.trim(),
          marks: Number(item.marks),
          difficulty: item.difficulty,
          question_type: 'Short Answer',
        })
        saved++
      }
      setMessage(`Successfully added ${saved} AI questions to the Question Bank!`)
      setMessageType('success')
      setAiQuestions([])
      setActiveTab('list')
      loadData()
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Error saving AI questions.')
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  const getSubjectName = (subId) => subjects.find((s) => s.id === subId)?.subject_name || `Subject #${subId}`
  const getUnitName = (uId) => units.find((u) => u.id === uId)?.unit_name || `Unit #${uId}`
  const getBloomName = (bId) => blooms.find((b) => b.id === bId)?.level_name || `Bloom #${bId}`

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header & Tabs */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">📚</span>
              <h1 className="text-2xl font-bold text-slate-800">Approved Question Bank</h1>
              <span className="bg-indigo-100 text-indigo-700 text-xs font-semibold px-2.5 py-0.5 rounded-full">
                {questions.length} Questions
              </span>
            </div>
            <p className="text-sm text-slate-500 mt-1">
              Curate, categorize, and bulk import verified questions used to automatically generate examination papers.
            </p>
          </div>

          <div className="flex flex-wrap gap-2 bg-slate-100 p-1.5 rounded-xl border border-slate-200">
            <button
              onClick={() => setActiveTab('list')}
              className={`px-4 py-2 text-xs font-semibold rounded-lg transition ${
                activeTab === 'list' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Browse Bank ({visibleQuestions.length})
            </button>
            <button
              onClick={() => setActiveTab('add')}
              className={`px-4 py-2 text-xs font-semibold rounded-lg transition ${
                activeTab === 'add' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              ➕ Add Question
            </button>
            <button
              onClick={() => setActiveTab('bulk')}
              className={`px-4 py-2 text-xs font-semibold rounded-lg transition ${
                activeTab === 'bulk' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              📥 Bulk CSV Import
            </button>
            <button
              onClick={() => setActiveTab('ai')}
              className={`px-4 py-2 text-xs font-semibold rounded-lg transition ${
                activeTab === 'ai' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              🤖 AI Question Drafter
            </button>
          </div>
        </div>

        {/* Global Alert Notification */}
        {message && (
          <div
            className={`p-4 rounded-xl border flex items-center justify-between gap-3 text-sm font-medium ${
              messageType === 'error'
                ? 'bg-red-50 border-red-200 text-red-700'
                : messageType === 'success'
                ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                : 'bg-blue-50 border-blue-200 text-blue-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <span>{messageType === 'error' ? '⚠️' : messageType === 'success' ? '✓' : 'ℹ️'}</span>
              <span>{message}</span>
            </div>
            <button onClick={() => setMessage('')} className="text-slate-400 hover:text-slate-600 text-lg leading-none">
              &times;
            </button>
          </div>
        )}

        {/* TAB 1: BROWSE QUESTION BANK */}
        {activeTab === 'list' && (
          <div className="space-y-4">
            {/* Filter Toolbar */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                {/* Search Bar */}
                <div className="md:col-span-4">
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">🔍</span>
                    <input
                      type="text"
                      className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      placeholder="Search questions by keyword, topic, or solution..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />
                  </div>
                </div>

                {/* Filter Subject */}
                <div>
                  <label className="text-xs font-semibold text-slate-500 uppercase block mb-1">Subject</label>
                  <select
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm focus:bg-white"
                    value={filterSubject}
                    onChange={(e) => {
                      setFilterSubject(e.target.value)
                      setFilterUnit('')
                    }}
                  >
                    <option value="">All Subjects</option>
                    {subjects.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.subject_name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Filter Unit */}
                <div>
                  <label className="text-xs font-semibold text-slate-500 uppercase block mb-1">Unit / Chapter</label>
                  <select
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm focus:bg-white"
                    value={filterUnit}
                    onChange={(e) => setFilterUnit(e.target.value)}
                  >
                    <option value="">All Units</option>
                    {filteredUnitsForFilter.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.unit_name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Filter Bloom */}
                <div>
                  <label className="text-xs font-semibold text-slate-500 uppercase block mb-1">Bloom Level</label>
                  <select
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm focus:bg-white"
                    value={filterBloom}
                    onChange={(e) => setFilterBloom(e.target.value)}
                  >
                    <option value="">All Bloom Levels</option>
                    {blooms.map((b) => (
                      <option key={b.id} value={b.id}>
                        {b.level_name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Filter Difficulty */}
                <div>
                  <label className="text-xs font-semibold text-slate-500 uppercase block mb-1">Difficulty</label>
                  <select
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm focus:bg-white"
                    value={filterDifficulty}
                    onChange={(e) => setFilterDifficulty(e.target.value)}
                  >
                    <option value="">All Difficulties</option>
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
              </div>

              {/* Reset Filters */}
              {(filterSubject || filterUnit || filterBloom || filterDifficulty || filterType || filterMarks || search) && (
                <div className="flex justify-between items-center pt-2 border-t border-slate-100 text-xs">
                  <span className="text-slate-500">
                    Showing <strong className="text-slate-800">{visibleQuestions.length}</strong> of {questions.length} questions
                  </span>
                  <button
                    onClick={() => {
                      setSearch('')
                      setFilterSubject('')
                      setFilterUnit('')
                      setFilterBloom('')
                      setFilterDifficulty('')
                      setFilterType('')
                      setFilterMarks('')
                    }}
                    className="text-indigo-600 hover:text-indigo-800 font-semibold"
                  >
                    Clear All Filters
                  </button>
                </div>
              )}
            </div>

            {/* Questions List */}
            {loading ? (
              <div className="p-12 text-center text-slate-400 bg-white rounded-2xl border">
                <div className="animate-spin inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mb-2" />
                <p>Loading question bank...</p>
              </div>
            ) : visibleQuestions.length === 0 ? (
              <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
                <p className="text-slate-500 text-base font-medium">No matching questions found in the Question Bank.</p>
                <p className="text-slate-400 text-sm mt-1">Try clearing your filters or click "Add Question" to insert new questions.</p>
              </div>
            ) : (
              <div className="grid gap-3">
                {visibleQuestions.map((q, idx) => (
                  <div
                    key={q.id}
                    className="bg-white rounded-xl p-5 border border-slate-200 hover:border-indigo-200 hover:shadow-sm transition space-y-3"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="space-y-1.5 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-slate-400">#{idx + 1}</span>
                          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700">
                            {getSubjectName(q.subject_id)}
                          </span>
                          <span className="text-xs font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                            {getUnitName(q.unit_id)}
                          </span>
                          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-50 text-purple-700">
                            {getBloomName(q.bloom_level_id)}
                          </span>
                          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-700">
                            {q.marks} {q.marks === 1 ? 'Mark' : 'Marks'}
                          </span>
                          <span
                            className={`text-xs font-semibold px-2 py-0.5 rounded capitalize ${
                              q.difficulty === 'easy'
                                ? 'bg-emerald-50 text-emerald-700'
                                : q.difficulty === 'hard'
                                ? 'bg-rose-50 text-rose-700'
                                : 'bg-blue-50 text-blue-700'
                            }`}
                          >
                            {q.difficulty}
                          </span>
                        </div>
                        <p className="text-slate-800 font-medium text-base leading-relaxed pt-1">
                          {q.question_text}
                        </p>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleStartEdit(q)}
                          className="px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-100 transition"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteQuestion(q.id)}
                          className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-rose-50 text-rose-600 hover:bg-rose-100 transition"
                        >
                          Delete
                        </button>
                      </div>
                    </div>

                    {/* Optional Solution / Explanation */}
                    {(q.answer || q.explanation) && (
                      <div className="pt-2 border-t border-slate-100 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs bg-slate-50 p-3 rounded-lg">
                        {q.answer && (
                          <div>
                            <span className="font-semibold text-slate-600 block">Answer / Solution:</span>
                            <span className="text-slate-800">{q.answer}</span>
                          </div>
                        )}
                        {q.explanation && (
                          <div>
                            <span className="font-semibold text-slate-600 block">Explanation / Rubric:</span>
                            <span className="text-slate-800">{q.explanation}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: ADD SINGLE QUESTION */}
        {activeTab === 'add' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm max-w-3xl mx-auto space-y-5">
            <div>
              <h2 className="text-lg font-bold text-slate-800">Add New Question to Bank</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Every approved question added here becomes immediately available to the paper generator.
              </p>
            </div>

            <form onSubmit={handleAddQuestion} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Subject *</label>
                  <select
                    className="w-full bg-slate-50 border rounded-xl px-3 py-2.5 text-sm"
                    value={form.subject_id}
                    onChange={(e) => setForm({ ...form, subject_id: e.target.value, unit_id: '' })}
                    required
                  >
                    <option value="">-- Select Subject --</option>
                    {subjects.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.subject_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Unit / Chapter *</label>
                  <select
                    className="w-full bg-slate-50 border rounded-xl px-3 py-2.5 text-sm"
                    value={form.unit_id}
                    onChange={(e) => setForm({ ...form, unit_id: e.target.value })}
                    required
                  >
                    <option value="">-- Select Unit --</option>
                    {filteredUnitsForAdd.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.unit_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Question Text *</label>
                <textarea
                  rows="3"
                  className="w-full bg-slate-50 border rounded-xl px-3 py-2.5 text-sm focus:bg-white"
                  placeholder="Enter the full question text..."
                  value={form.question_text}
                  onChange={(e) => setForm({ ...form, question_text: e.target.value })}
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Bloom Level *</label>
                  <select
                    className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"
                    value={form.bloom_level_id}
                    onChange={(e) => setForm({ ...form, bloom_level_id: e.target.value })}
                    required
                  >
                    {blooms.map((b) => (
                      <option key={b.id} value={b.id}>
                        {b.level_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Question Type</label>
                  <select
                    className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"
                    value={form.question_type}
                    onChange={(e) => setForm({ ...form, question_type: e.target.value })}
                  >
                    <option value="Short Answer">Short Answer</option>
                    <option value="MCQ">MCQ</option>
                    <option value="Long Answer">Long Answer</option>
                    <option value="Descriptive">Descriptive</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Marks *</label>
                  <input
                    type="number"
                    min="1"
                    className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"
                    value={form.marks}
                    onChange={(e) => setForm({ ...form, marks: e.target.value })}
                    required
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Difficulty</label>
                  <select
                    className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"
                    value={form.difficulty}
                    onChange={(e) => setForm({ ...form, difficulty: e.target.value })}
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Answer / Solution (Optional)</label>
                  <textarea
                    rows="2"
                    className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm focus:bg-white"
                    placeholder="Provide sample solution or key..."
                    value={form.answer}
                    onChange={(e) => setForm({ ...form, answer: e.target.value })}
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Explanation / Rubric (Optional)</label>
                  <textarea
                    rows="2"
                    className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm focus:bg-white"
                    placeholder="Provide marking criteria or notes..."
                    value={form.explanation}
                    onChange={(e) => setForm({ ...form, explanation: e.target.value })}
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setActiveTab('list')}
                  className="px-5 py-2.5 text-xs font-semibold rounded-xl border text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2.5 text-xs font-semibold rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm transition"
                >
                  Save to Question Bank
                </button>
              </div>
            </form>
          </div>
        )}

        {/* TAB 3: BULK CSV / JSON IMPORT */}
        {activeTab === 'bulk' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm max-w-4xl mx-auto space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-800">Bulk Import Questions</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Import dozens of approved questions in seconds via CSV or JSON.
              </p>
            </div>

            <div className="bg-slate-50 border rounded-xl p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-700 uppercase">Standard CSV Format Sample</span>
                <button
                  onClick={() => setBulkCsvText(sampleCsvTemplate)}
                  className="text-xs text-indigo-600 font-semibold hover:underline"
                >
                  Load Sample Template
                </button>
              </div>
              <pre className="text-xs bg-white p-3 rounded-lg border text-slate-600 overflow-x-auto">
                {sampleCsvTemplate}
              </pre>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-700 block">
                Paste CSV or JSON Data Below
              </label>
              <textarea
                rows="8"
                className="w-full bg-slate-50 font-mono text-xs border rounded-xl p-3 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Paste CSV rows or JSON array here..."
                value={bulkCsvText}
                onChange={(e) => setBulkCsvText(e.target.value)}
              />
            </div>

            <div className="flex justify-end gap-3">
              <button
                disabled={bulkUploading}
                onClick={handleBulkUpload}
                className="px-6 py-2.5 text-xs font-semibold rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm transition disabled:opacity-50"
              >
                {bulkUploading ? 'Validating & Importing...' : 'Import to Question Bank'}
              </button>
            </div>

            {/* Validation & Error Report */}
            {bulkResult && (
              <div className="pt-4 border-t space-y-3">
                <h3 className="text-sm font-bold text-slate-800">Import Summary</h3>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="bg-slate-50 p-3 rounded-xl border">
                    <span className="text-xs text-slate-500 block">Submitted</span>
                    <strong className="text-base text-slate-800">{bulkResult.total_submitted}</strong>
                  </div>
                  <div className="bg-emerald-50 p-3 rounded-xl border border-emerald-200">
                    <span className="text-xs text-emerald-600 block">Successfully Added</span>
                    <strong className="text-base text-emerald-700">{bulkResult.successful_count}</strong>
                  </div>
                  <div className="bg-rose-50 p-3 rounded-xl border border-rose-200">
                    <span className="text-xs text-rose-600 block">Failed / Invalid</span>
                    <strong className="text-base text-rose-700">{bulkResult.failed_count}</strong>
                  </div>
                </div>

                {bulkResult.errors?.length > 0 && (
                  <div className="space-y-2 mt-3">
                    <h4 className="text-xs font-bold text-rose-700 uppercase">Row Validation Errors:</h4>
                    <div className="space-y-1.5 max-h-48 overflow-y-auto">
                      {bulkResult.errors.map((err, idx) => (
                        <div key={idx} className="text-xs bg-rose-50 border border-rose-200 p-2.5 rounded-lg text-rose-800">
                          <strong>Row {err.row_index}:</strong> {err.error} <span className="text-rose-500 italic">("{err.question_text}")</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 4: AI QUESTION DRAFTER */}
        {activeTab === 'ai' && (
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm max-w-4xl mx-auto space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-800">AI Question Drafter (Google Gemini)</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Draft new questions using Gemini AI, review and edit them, then save them into your approved Question Bank.
              </p>
            </div>

            <form onSubmit={handleAIGenerate} className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Subject</label>
                <select
                  className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"
                  value={aiForm.subject_id}
                  onChange={(e) => setAiForm({ ...aiForm, subject_id: e.target.value, unit_id: '' })}
                  required
                >
                  <option value="">-- Select Subject --</option>
                  {subjects.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.subject_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Unit</label>
                <select
                  className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"
                  value={aiForm.unit_id}
                  onChange={(e) => setAiForm({ ...aiForm, unit_id: e.target.value })}
                  required
                >
                  <option value="">-- Select Unit --</option>
                  {filteredUnitsForAI.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.unit_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Bloom Level</label>
                <select
                  className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"
                  value={aiForm.bloom_level_id}
                  onChange={(e) => setAiForm({ ...aiForm, bloom_level_id: e.target.value })}
                  required
                >
                  {blooms.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.level_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Marks</label>
                <input
                  type="number"
                  min="1"
                  className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"
                  value={aiForm.marks}
                  onChange={(e) => setAiForm({ ...aiForm, marks: e.target.value })}
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Difficulty</label>
                <select
                  className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"
                  value={aiForm.difficulty}
                  onChange={(e) => setAiForm({ ...aiForm, difficulty: e.target.value })}
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Count</label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"
                  value={aiForm.count}
                  onChange={(e) => setAiForm({ ...aiForm, count: e.target.value })}
                />
              </div>

              <div className="md:col-span-3">
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Textbook Context / Notes (Optional)
                </label>
                <textarea
                  rows="3"
                  className="w-full bg-slate-50 border rounded-xl p-3 text-sm focus:bg-white"
                  placeholder="Paste relevant chapter notes or textbook passages for targeted questions..."
                  value={aiForm.textbook_context}
                  onChange={(e) => setAiForm({ ...aiForm, textbook_context: e.target.value })}
                />
              </div>

              <div className="md:col-span-3 flex justify-end">
                <button
                  type="submit"
                  disabled={aiGenerating}
                  className="px-6 py-2.5 text-xs font-semibold rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm transition disabled:opacity-50"
                >
                  {aiGenerating ? 'Drafting Questions...' : 'Draft Questions with AI'}
                </button>
              </div>
            </form>

            {/* AI Generated Questions Preview */}
            {aiQuestions.length > 0 && (
              <div className="pt-4 border-t space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-800">Drafted Questions: Review & Save</h3>
                  <span className="text-xs text-slate-500">Check the questions you want to add to the bank</span>
                </div>

                <div className="space-y-3">
                  {aiQuestions.map((q, idx) => (
                    <div key={idx} className="flex items-start gap-3 p-4 bg-slate-50 border rounded-xl">
                      <input
                        type="checkbox"
                        checked={q.selected}
                        onChange={() => {
                          const next = [...aiQuestions]
                          next[idx].selected = !next[idx].selected
                          setAiQuestions(next)
                        }}
                        className="mt-1 h-4 w-4 rounded text-indigo-600 focus:ring-indigo-500"
                      />
                      <div className="flex-1 space-y-2">
                        <textarea
                          rows="2"
                          className="w-full bg-white border rounded-lg p-2 text-sm text-slate-800"
                          value={q.question_text}
                          onChange={(e) => {
                            const next = [...aiQuestions]
                            next[idx].question_text = e.target.value
                            setAiQuestions(next)
                          }}
                        />
                        <div className="flex gap-2 text-xs">
                          <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-semibold">
                            {q.marks} Marks
                          </span>
                          <span className="px-2 py-0.5 rounded bg-slate-200 text-slate-700 font-semibold capitalize">
                            {q.difficulty}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex justify-end">
                  <button
                    onClick={handleSaveAIQuestions}
                    className="px-6 py-2.5 text-xs font-semibold rounded-xl bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm transition"
                  >
                    Save Selected to Question Bank
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* EDIT MODAL */}
        {editingQuestion && (
          <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xl max-w-2xl w-full space-y-4">
              <div className="flex justify-between items-center pb-2 border-b">
                <h3 className="text-base font-bold text-slate-800">Edit Question #{editForm.id}</h3>
                <button onClick={() => setEditingQuestion(null)} className="text-slate-400 hover:text-slate-600 text-lg">
                  &times;
                </button>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Question Text</label>
                  <textarea
                    rows="3"
                    className="w-full bg-slate-50 border rounded-xl p-2.5 text-sm"
                    value={editForm.question_text}
                    onChange={(e) => setEditForm({ ...editForm, question_text: e.target.value })}
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">Marks</label>
                    <input
                      type="number"
                      min="1"
                      className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"
                      value={editForm.marks}
                      onChange={(e) => setEditForm({ ...editForm, marks: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">Difficulty</label>
                    <select
                      className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"
                      value={editForm.difficulty}
                      onChange={(e) => setEditForm({ ...editForm, difficulty: e.target.value })}
                    >
                      <option value="easy">Easy</option>
                      <option value="medium">Medium</option>
                      <option value="hard">Hard</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">Answer (Optional)</label>
                    <textarea
                      rows="2"
                      className="w-full bg-slate-50 border rounded-xl p-2 text-xs"
                      value={editForm.answer}
                      onChange={(e) => setEditForm({ ...editForm, answer: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">Explanation (Optional)</label>
                    <textarea
                      rows="2"
                      className="w-full bg-slate-50 border rounded-xl p-2 text-xs"
                      value={editForm.explanation}
                      onChange={(e) => setEditForm({ ...editForm, explanation: e.target.value })}
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t">
                <button
                  onClick={() => setEditingQuestion(null)}
                  className="px-4 py-2 text-xs font-semibold rounded-xl border text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveEdit}
                  className="px-5 py-2 text-xs font-semibold rounded-xl bg-indigo-600 text-white hover:bg-indigo-700"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

export default Questions
