import { Link } from 'react-router-dom'

const Home = () => {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col justify-center px-6 py-16">
        <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
          <div>
            <p className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">AQPG</p>
            <h1 className="mb-4 text-4xl font-semibold sm:text-5xl">Automated Question Paper Generation</h1>
            <p className="mb-8 max-w-2xl text-lg text-slate-600">
              Build a question bank, organize subjects and units, and generate balanced papers in seconds.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link to="/register" className="rounded-lg bg-slate-900 px-5 py-3 font-medium text-white">Create account</Link>
              <Link to="/login" className="rounded-lg border border-slate-300 px-5 py-3 font-medium text-slate-900">Login</Link>
            </div>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="mb-3 text-2xl font-semibold">What you can do</h2>
            <ul className="space-y-3 text-slate-700">
              <li>• Manage subjects, units, Bloom levels, and questions</li>
              <li>• Generate question papers with marks and Bloom weighting</li>
              <li>• Review generated papers from a central dashboard</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
