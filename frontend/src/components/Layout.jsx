import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { clearToken } from '../api'

const Layout = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const [dark, setDark] = useState(localStorage.getItem('theme') === 'dark')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }, [dark])

  const logout = () => {
    clearToken()
    navigate('/login', { replace: true })
  }

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/curriculum', label: 'Curriculum', icon: '🌐' },
    { path: '/subjects', label: 'Subjects', icon: '📚' },
    { path: '/units', label: 'Units', icon: '📝' },
    { path: '/bloom-levels', label: 'Bloom Levels', icon: '🧠' },
    { path: '/questions', label: 'Questions Bank', icon: '📂' },
    { path: '/generate-paper', label: 'Generate Paper', icon: '⚙️' },
    { path: '/generated-papers', label: 'Generated Papers', icon: '📄' },
  ]


  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100 transition-colors duration-300 font-sans">
      {/* Sidebar for Desktop */}
      <aside className="hidden md:flex flex-col w-64 bg-slate-900 dark:bg-slate-950 text-slate-300 border-r border-slate-800 p-5 shrink-0">
        <div className="flex items-center gap-3 mb-8">
          <span className="text-3xl">🎯</span>
          <div>
            <h2 className="text-lg font-bold text-white leading-tight">AQPG Platform</h2>
            <span className="text-xs text-emerald-400 font-medium font-sans">Teacher Console</span>
          </div>
        </div>

        <nav className="flex-1 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition ${isActive ? 'bg-slate-850 text-white shadow-sm font-semibold' : 'hover:bg-slate-800/50 hover:text-white'}`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>

        <div className="border-t border-slate-800 pt-4 space-y-2">
          {/* Theme toggle switcher */}
          <button
            onClick={() => setDark(!dark)}
            className="flex items-center justify-between w-full px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-slate-800 transition"
          >
            <div className="flex items-center gap-3">
              <span>{dark ? '🌙' : '☀️'}</span>
              <span>{dark ? 'Dark Mode' : 'Light Mode'}</span>
            </div>
            <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded">Switch</span>
          </button>
          
          <button
            onClick={logout}
            className="flex items-center gap-3 w-full px-4 py-2.5 rounded-xl text-sm font-medium text-rose-400 hover:bg-rose-500/10 transition"
          >
            <span>🚪</span>
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main content wrapper */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar for mobile */}
        <header className="md:hidden flex items-center justify-between bg-slate-900 text-white p-4">
          <div className="flex items-center gap-3">
            <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="text-2xl focus:outline-none">
              ☰
            </button>
            <h2 className="text-lg font-bold">AQPG Console</h2>
          </div>
          <button onClick={() => setDark(!dark)} className="text-xl">
            {dark ? '🌙' : '☀️'}
          </button>
        </header>

        {/* Mobile menu drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden fixed inset-0 z-40 flex">
            <div className="fixed inset-0 bg-black/60" onClick={() => setMobileMenuOpen(false)}></div>
            <div className="relative flex flex-col w-64 max-w-xs bg-slate-900 text-slate-300 p-5">
              <div className="flex items-center gap-3 mb-6">
                <span className="text-3xl">🎯</span>
                <div>
                  <h2 className="text-lg font-bold text-white leading-tight">AQPG Platform</h2>
                  <span className="text-xs text-emerald-400 font-medium font-sans">Teacher Console</span>
                </div>
              </div>
              <nav className="flex-1 space-y-1">
                {navItems.map((item) => {
                  const isActive = location.pathname === item.path
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setMobileMenuOpen(false)}
                      className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition ${isActive ? 'bg-slate-800 text-white shadow-sm font-semibold' : 'hover:bg-slate-800/50 hover:text-white'}`}
                    >
                      <span>{item.icon}</span>
                      <span>{item.label}</span>
                    </Link>
                  )
                })}
              </nav>
              <div className="border-t border-slate-800 pt-4 space-y-2">
                <button
                  onClick={() => setDark(!dark)}
                  className="flex items-center justify-between w-full px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-slate-800 transition"
                >
                  <div className="flex items-center gap-3">
                    <span>{dark ? '🌙' : '☀️'}</span>
                    <span>{dark ? 'Dark Mode' : 'Light Mode'}</span>
                  </div>
                </button>
                <button
                  onClick={logout}
                  className="flex items-center gap-3 w-full px-4 py-2.5 rounded-xl text-sm font-medium text-rose-400 hover:bg-rose-500/10 transition"
                >
                  <span>🚪</span>
                  <span>Logout</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout
