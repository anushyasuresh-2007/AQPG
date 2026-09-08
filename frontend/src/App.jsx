import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { isAuthenticated } from './api'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Curriculum from './pages/Curriculum'
import Dashboard from './pages/Dashboard'
import Subjects from './pages/Subjects'
import Units from './pages/Units'
import BloomLevels from './pages/BloomLevels'
import Questions from './pages/Questions'
import GeneratePaper from './pages/GeneratePaper'
import GeneratedPapers from './pages/GeneratedPapers'
import Layout from './components/Layout'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('AQPG Application Error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-slate-800 p-8 rounded-2xl border border-red-800 shadow-2xl text-center space-y-4">
            <div className="text-4xl">⚠️</div>
            <h2 className="text-xl font-bold text-red-400">Something went wrong</h2>
            <p className="text-xs text-slate-300 bg-slate-950 p-3 rounded-lg font-mono text-left overflow-auto max-h-32">
              {this.state.error?.toString()}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null })
                window.location.reload()
              }}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold rounded-xl transition"
            >
              🔄 Reload Application
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

const ProtectedRoute = ({ children }) => {
  return isAuthenticated() ? children : <Navigate to='/login' replace />
}

const PublicRoute = ({ children }) => {
  return !isAuthenticated() ? children : <Navigate to='/dashboard' replace />
}

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<Home />} />
          <Route path='/login' element={<PublicRoute><Login /></PublicRoute>} />
          <Route path='/register' element={<PublicRoute><Register /></PublicRoute>} />
          <Route path='/dashboard' element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>} />
          <Route path='/curriculum' element={<ProtectedRoute><Layout><Curriculum /></Layout></ProtectedRoute>} />
          <Route path='/subjects' element={<ProtectedRoute><Layout><Subjects /></Layout></ProtectedRoute>} />
          <Route path='/units' element={<ProtectedRoute><Layout><Units /></Layout></ProtectedRoute>} />
          <Route path='/bloom-levels' element={<ProtectedRoute><Layout><BloomLevels /></Layout></ProtectedRoute>} />
          <Route path='/questions' element={<ProtectedRoute><Layout><Questions /></Layout></ProtectedRoute>} />
          <Route path='/generate-paper' element={<ProtectedRoute><Layout><GeneratePaper /></Layout></ProtectedRoute>} />
          <Route path='/generated-papers' element={<ProtectedRoute><Layout><GeneratedPapers /></Layout></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
