import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api, { setToken } from '../api'

const Login = () => {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    try {
      const response = await api.post('/login', form)
      setToken(response.data.access_token)
      navigate('/dashboard', { replace: true })
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 p-6 flex items-center justify-center">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold mb-2">Login</h1>
        <p className="text-slate-600 mb-6">Sign in to manage your question bank.</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input className="w-full rounded-lg border px-3 py-2" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="w-full rounded-lg border px-3 py-2" type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          {message ? <p className="text-sm text-red-600">{message}</p> : null}
          <button className="w-full rounded-lg bg-slate-900 px-4 py-2 font-medium text-white" disabled={loading}>{loading ? 'Signing in...' : 'Login'}</button>
        </form>
        <p className="mt-4 text-sm text-slate-600">No account? <Link to="/register" className="text-slate-900 font-medium">Register</Link></p>
      </div>
    </div>
  )
}

export default Login
