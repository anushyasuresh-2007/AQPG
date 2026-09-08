import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'

const Dashboard = () => {
  const [stats, setStats] = useState({ subjects: 0, units: 0, questions: 0 })
  const [subjectDist, setSubjectDist] = useState([])
  const [bloomDist, setBloomDist] = useState([])
  const [difficultyDist, setDifficultyDist] = useState({ easy: 0, medium: 0, hard: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [subRes, unitRes, questionRes, bloomRes] = await Promise.all([
          api.get('/subjects'),
          api.get('/units'),
          api.get('/questions'),
          api.get('/bloom-levels'),
        ])
        
        const subjects = subRes.data
        const units = unitRes.data
        const questions = questionRes.data
        const blooms = bloomRes.data

        setStats({
          subjects: subjects.length,
          units: units.length,
          questions: questions.length
        })

        // Subject distribution
        const subCounts = subjects.map(s => {
          const count = questions.filter(q => q.subject_id === s.id).length
          return { name: s.subject_name, count }
        }).sort((a, b) => b.count - a.count)
        setSubjectDist(subCounts)

        // Bloom distribution
        const bloomCounts = blooms.map(b => {
          const count = questions.filter(q => q.bloom_level_id === b.id).length
          return { name: b.level_name, count }
        })
        setBloomDist(bloomCounts)

        // Difficulty distribution
        const diffCounts = {
          easy: questions.filter(q => q.difficulty === 'easy').length,
          medium: questions.filter(q => q.difficulty === 'medium').length,
          hard: questions.filter(q => q.difficulty === 'hard').length,
        }
        setDifficultyDist(diffCounts)

      } catch (error) {
        console.error('Error loading dashboard stats:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  // Calculate difficulty percentages for Donut chart
  const totalDiff = difficultyDist.easy + difficultyDist.medium + difficultyDist.hard
  const easyPct = totalDiff > 0 ? (difficultyDist.easy / totalDiff) * 100 : 0
  const medPct = totalDiff > 0 ? (difficultyDist.medium / totalDiff) * 100 : 0
  const hardPct = totalDiff > 0 ? (difficultyDist.hard / totalDiff) * 100 : 0

  // Donut chart stroke math
  const radius = 50
  const circumference = 2 * Math.PI * radius
  const easyStroke = (easyPct / 100) * circumference
  const medStroke = (medPct / 100) * circumference
  const hardStroke = (hardPct / 100) * circumference

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-6">
      <div className="mx-auto max-w-6xl">
        
        {/* Welcome Header */}
        <div className="mb-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white">AQPG Platform Overview</h1>
          <p className="text-sm text-slate-500 mt-1">Manage curricular modules, populate the question bank, and build blueprint papers.</p>
        </div>

        {loading ? (
          <div className="py-12 text-center text-slate-500">Loading analytics dashboard...</div>
        ) : (
          <>
            {/* Stats Cards */}
            <div className="grid gap-4 grid-cols-1 md:grid-cols-3">
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white p-6 shadow-sm flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Subjects</p>
                  <p className="text-3xl font-bold text-slate-800 dark:text-white mt-1">{stats.subjects}</p>
                </div>
                <span className="text-3xl bg-blue-50 dark:bg-blue-900/20 p-3 rounded-2xl">📚</span>
              </div>
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white p-6 shadow-sm flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Syllabus Units</p>
                  <p className="text-3xl font-bold text-slate-800 dark:text-white mt-1">{stats.units}</p>
                </div>
                <span className="text-3xl bg-indigo-50 dark:bg-indigo-900/20 p-3 rounded-2xl">📝</span>
              </div>
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white p-6 shadow-sm flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Stored Questions</p>
                  <p className="text-3xl font-bold text-slate-800 dark:text-white mt-1">{stats.questions}</p>
                </div>
                <span className="text-3xl bg-emerald-50 dark:bg-emerald-900/20 p-3 rounded-2xl">📂</span>
              </div>
            </div>

            {/* Graphs Grid */}
            <div className="mt-6 grid gap-6 md:grid-cols-2">
              
              {/* Questions per Subject (Horizontal bar chart) */}
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white p-6 shadow-sm">
                <h3 className="text-md font-semibold text-slate-800 dark:text-white mb-4">Questions per Subject</h3>
                {subjectDist.length === 0 ? (
                  <p className="text-sm text-slate-500 italic py-6">No subjects created yet.</p>
                ) : (
                  <div className="space-y-4">
                    {subjectDist.map((sub, idx) => {
                      const maxVal = Math.max(...subjectDist.map(s => s.count), 1)
                      const pct = (sub.count / maxVal) * 100
                      return (
                        <div key={idx} className="space-y-1">
                          <div className="flex justify-between text-xs font-medium">
                            <span className="text-slate-700 dark:text-slate-300">{sub.name}</span>
                            <span className="text-slate-500">{sub.count} Questions</span>
                          </div>
                          <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2">
                            <div className="bg-blue-600 h-2 rounded-full transition-all duration-500" style={{ width: `${pct}%` }}></div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>

              {/* Cognitive / Bloom levels taxonomy breakdown */}
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white p-6 shadow-sm">
                <h3 className="text-md font-semibold text-slate-800 dark:text-white mb-4">Bloom's Taxonomy Spread</h3>
                {bloomDist.length === 0 ? (
                  <p className="text-sm text-slate-500 italic py-6">No Bloom levels configured.</p>
                ) : (
                  <div className="grid grid-cols-2 gap-4">
                    {bloomDist.map((b, idx) => {
                      const maxVal = Math.max(...bloomDist.map(bl => bl.count), 1)
                      const pct = (b.count / maxVal) * 100
                      return (
                        <div key={idx} className="border dark:border-slate-800 p-3 rounded-xl bg-slate-50 dark:bg-slate-850">
                          <p className="text-xs text-slate-500 font-semibold truncate capitalize">{b.name}</p>
                          <div className="flex items-baseline gap-2 mt-1">
                            <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400">{b.count}</span>
                            <span className="text-[10px] text-slate-400">items</span>
                          </div>
                          <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-1.5 mt-2">
                            <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: `${pct}%` }}></div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>

              {/* Difficulty Breakdown (SVG Donut Chart) */}
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white p-6 shadow-sm md:col-span-2 flex flex-col md:flex-row items-center gap-8">
                <div className="flex-1">
                  <h3 className="text-md font-semibold text-slate-800 dark:text-white mb-2">Question Difficulty Distribution</h3>
                  <p className="text-xs text-slate-500">Breakdown of content difficulty classifications currently saved in the database.</p>
                  
                  <div className="mt-6 space-y-3">
                    <div className="flex items-center gap-3">
                      <span className="w-3.5 h-3.5 rounded-full bg-emerald-500 shrink-0"></span>
                      <span className="text-sm font-medium flex-1 text-slate-700 dark:text-slate-300">Easy</span>
                      <span className="text-sm font-semibold">{difficultyDist.easy} ({easyPct.toFixed(1)}%)</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="w-3.5 h-3.5 rounded-full bg-amber-500 shrink-0"></span>
                      <span className="text-sm font-medium flex-1 text-slate-700 dark:text-slate-300">Medium</span>
                      <span className="text-sm font-semibold">{difficultyDist.medium} ({medPct.toFixed(1)}%)</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="w-3.5 h-3.5 rounded-full bg-rose-500 shrink-0"></span>
                      <span className="text-sm font-medium flex-1 text-slate-700 dark:text-slate-300">Hard</span>
                      <span className="text-sm font-semibold">{difficultyDist.hard} ({hardPct.toFixed(1)}%)</span>
                    </div>
                  </div>
                </div>

                {/* SVG Donut Circle */}
                <div className="relative w-48 h-48 flex items-center justify-center shrink-0">
                  <svg width="100%" height="100%" viewBox="0 0 120 120" className="transform -rotate-90">
                    <circle cx="60" cy="60" r="50" fill="transparent" stroke="#e2e8f0" strokeWidth="12" className="dark:stroke-slate-800" />
                    {totalDiff > 0 ? (
                      <>
                        {/* Easy Segment */}
                        <circle
                          cx="60"
                          cy="60"
                          r="50"
                          fill="transparent"
                          stroke="#10b981"
                          strokeWidth="12"
                          strokeDasharray={`${easyStroke} ${circumference}`}
                          strokeDashoffset="0"
                          className="transition-all duration-700"
                        />
                        {/* Medium Segment */}
                        <circle
                          cx="60"
                          cy="60"
                          r="50"
                          fill="transparent"
                          stroke="#f59e0b"
                          strokeWidth="12"
                          strokeDasharray={`${medStroke} ${circumference}`}
                          strokeDashoffset={`-${easyStroke}`}
                          className="transition-all duration-700"
                        />
                        {/* Hard Segment */}
                        <circle
                          cx="60"
                          cy="60"
                          r="50"
                          fill="transparent"
                          stroke="#ef4444"
                          strokeWidth="12"
                          strokeDasharray={`${hardStroke} ${circumference}`}
                          strokeDashoffset={`-${easyStroke + medStroke}`}
                          className="transition-all duration-700"
                        />
                      </>
                    ) : null}
                  </svg>
                  <div className="absolute text-center">
                    <p className="text-2xl font-bold text-slate-800 dark:text-white">{totalDiff}</p>
                    <p className="text-[10px] uppercase font-semibold text-slate-400">Total Items</p>
                  </div>
                </div>
              </div>

            </div>

            {/* Quick Links Nav */}
            <div className="mt-8">
              <h3 className="text-lg font-semibold text-slate-850 dark:text-slate-200 mb-4">Quick Navigation</h3>
              <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
                {[
                  { route: 'subjects', name: 'Subjects Catalog', desc: 'Manage exam topics and classes.', icon: '📚' },
                  { route: 'questions', name: 'Questions Bank', desc: 'Create, edit and generate questions.', icon: '📂' },
                  { route: 'generate-paper', name: 'Generate Exam', desc: 'Create blueprint paper documents.', icon: '⚙️' },
                  { route: 'generated-papers', name: 'Exam History', desc: 'View previously prepared exams.', icon: '📄' },
                ].map((link) => (
                  <Link key={link.route} to={`/${link.route}`} className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 flex flex-col justify-between">
                    <div>
                      <span className="text-2xl">{link.icon}</span>
                      <h4 className="text-sm font-bold text-slate-800 dark:text-white mt-2 leading-tight">{link.name}</h4>
                      <p className="text-[11px] text-slate-400 mt-1 leading-snug">{link.desc}</p>
                    </div>
                    <span className="text-xs text-blue-600 dark:text-blue-400 font-semibold mt-4 block">Open Module →</span>
                  </Link>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default Dashboard
