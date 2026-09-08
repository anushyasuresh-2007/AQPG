import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api from '../api'

const Register = () => {
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'teacher' })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    try {
      await api.post('/register', form)
      setMessage('Registration successful. Please log in.')
      navigate('/login')
    } catch (error) {
      setMessage(error?.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 p-6 flex items-center justify-center">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold mb-2">Register</h1>
        <p className="text-slate-600 mb-6">Create a new AQPG account.</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input className="w-full rounded-lg border px-3 py-2" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input className="w-full rounded-lg border px-3 py-2" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="w-full rounded-lg border px-3 py-2" type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <select className="w-full rounded-lg border px-3 py-2" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="teacher">Teacher</option>
            <option value="admin">Admin</option>
          </select>
          {message ? <p className="text-sm text-red-600">{message}</p> : null}
          <button className="w-full rounded-lg bg-slate-900 px-4 py-2 font-medium text-white" disabled={loading}>{loading ? 'Creating account...' : 'Register'}</button>
        </form>
        <p className="mt-4 text-sm text-slate-600">Already have an account? <Link to="/login" className="text-slate-900 font-medium">Login</Link></p>
      </div>
    </div>
  )
}

export default Register
