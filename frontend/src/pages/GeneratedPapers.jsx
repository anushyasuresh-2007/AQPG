import React, { useState, useEffect } from "react";
import api from "../api";


export default function GeneratedPapers() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [selectedPaper, setSelectedPaper] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  const fetchPapers = async () => {
    try {
      setLoading(true);
      const res = await api.get("/generated-papers");
      setPapers(res.data || []);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load saved papers");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, []);

  const handleView = async (paperId) => {
    try {
      setPreviewLoading(true);
      const res = await api.get(`/generated-papers/${paperId}`);
      setSelectedPaper(res.data);
    } catch (err) {
      alert("Failed to load paper details");
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleDelete = async (paperId) => {
    if (!window.confirm("Are you sure you want to delete this question paper?")) return;
    try {
      await api.delete(`/generated-papers/${paperId}`);
      setPapers((prev) => prev.filter((p) => p.paper_id !== paperId && p.id !== paperId));
      if (selectedPaper && (selectedPaper.paper_id === paperId || selectedPaper.id === paperId)) {
        setSelectedPaper(null);
      }
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to delete question paper");
    }
  };

  const downloadFile = (url, filename) => {
    const token = localStorage.getItem("token");
    fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Export failed");
        return res.blob();
      })
      .then((blob) => {
        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
      })
      .catch((e) => alert("Failed to download file: " + e.message));
  };

  const filteredPapers = papers.filter((p) => {
    const match =
      p.title?.toLowerCase().includes(search.toLowerCase()) ||
      p.board_name?.toLowerCase().includes(search.toLowerCase()) ||
      p.subject_name?.toLowerCase().includes(search.toLowerCase()) ||
      p.class_name?.toLowerCase().includes(search.toLowerCase()) ||
      p.paper_id?.toLowerCase().includes(search.toLowerCase());
    return match;
  });

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 md:p-10">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400">
              📁 Generated Question Papers
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Browse, view, and export past AI-generated and question bank examination papers.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchPapers}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-medium border border-slate-700 transition"
            >
              🔄 Refresh
            </button>
            <a
              href="/generate-paper"
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-lg text-sm font-semibold shadow-lg shadow-blue-500/20 transition"
            >
              ⚡ Create New Paper
            </a>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex items-center gap-3 bg-slate-800/80 p-3 rounded-xl border border-slate-700">
          <span className="text-slate-400 text-lg ml-2">🔍</span>
          <input
            type="text"
            placeholder="Search by title, board, class, subject, or paper ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-transparent border-none text-slate-100 placeholder-slate-400 focus:outline-none text-sm"
          />
          {search && (
            <button
              onClick={() => setSearch("")}
              className="text-xs text-slate-400 hover:text-white px-2 py-1 bg-slate-700 rounded"
            >
              Clear
            </button>
          )}
        </div>

        {error && (
          <div className="p-4 bg-red-950/60 border border-red-800 rounded-xl text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* Papers Table */}
        {loading ? (
          <div className="text-center py-20 text-slate-400">
            <div className="inline-block animate-spin text-3xl mb-3">⌛</div>
            <p>Loading generated examination papers...</p>
          </div>
        ) : filteredPapers.length === 0 ? (
          <div className="text-center py-16 bg-slate-800/40 rounded-2xl border border-slate-800">
            <div className="text-4xl mb-3">📄</div>
            <p className="text-slate-300 font-semibold">No Question Papers Found</p>
            <p className="text-slate-500 text-sm mt-1">
              Generate a new paper using the AI examination generator.
            </p>
            <a
              href="/generate-paper"
              className="inline-block mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium"
            >
              Generate First Paper
            </a>
          </div>
        ) : (
          <div className="overflow-x-auto bg-slate-800/60 rounded-2xl border border-slate-800 shadow-xl">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800 text-slate-400 text-xs uppercase font-semibold border-b border-slate-700">
                <tr>
                  <th className="p-4">Paper ID & Title</th>
                  <th className="p-4">Board & Class</th>
                  <th className="p-4">Subject</th>
                  <th className="p-4 text-center">Marks</th>
                  <th className="p-4 text-center">Questions</th>
                  <th className="p-4">Source</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filteredPapers.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-700/30 transition">
                    <td className="p-4">
                      <div className="font-bold text-white">{p.title}</div>
                      <div className="text-xs text-slate-400 font-mono mt-0.5">{p.paper_id}</div>
                    </td>
                    <td className="p-4">
                      <span className="inline-block bg-blue-950/80 text-blue-300 text-xs px-2 py-0.5 rounded mr-1.5 font-medium border border-blue-800/60">
                        {p.board_name}
                      </span>
                      <span className="text-slate-300">{p.class_name}</span>
                    </td>
                    <td className="p-4 text-slate-200 font-medium">{p.subject_name}</td>
                    <td className="p-4 text-center font-bold text-emerald-400">{p.total_marks}</td>
                    <td className="p-4 text-center font-medium text-slate-300">{p.total_questions}</td>
                    <td className="p-4">
                      <span
                        className={`text-xs px-2 py-0.5 rounded font-medium ${
                          p.source === "Hybrid"
                            ? "bg-purple-950 text-purple-300 border border-purple-800"
                            : p.source === "Ai" || p.source === "Ai generator"
                            ? "bg-indigo-950 text-indigo-300 border border-indigo-800"
                            : "bg-emerald-950 text-emerald-300 border border-emerald-800"
                        }`}
                      >
                        {p.source}
                      </span>
                    </td>
                    <td className="p-4 text-right space-x-2 whitespace-nowrap">
                      <button
                        onClick={() => handleView(p.paper_id)}
                        className="px-2.5 py-1.5 bg-blue-600/80 hover:bg-blue-600 text-white rounded text-xs font-medium transition"
                        title="View Paper Details"
                      >
                        👁️ View
                      </button>
                      <button
                        onClick={() =>
                          downloadFile(
                            `http://127.0.0.1:8011/api/v1/generated-papers/${p.paper_id}/docx`,
                            `${p.paper_id}.docx`
                          )
                        }
                        className="px-2.5 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded text-xs font-medium border border-slate-600 transition"
                        title="Download Word (.docx)"
                      >
                        📄 Word
                      </button>
                      <button
                        onClick={() =>
                          downloadFile(
                            `http://127.0.0.1:8011/api/v1/generated-papers/${p.paper_id}/pdf`,
                            `${p.paper_id}_Exam.pdf`
                          )
                        }
                        className="px-2.5 py-1.5 bg-emerald-700/80 hover:bg-emerald-600 text-white rounded text-xs font-medium transition"
                        title="Download Student PDF"
                      >
                        📥 PDF
                      </button>
                      <button
                        onClick={() => handleDelete(p.paper_id)}
                        className="px-2.5 py-1.5 bg-red-900/60 hover:bg-red-700 text-red-200 rounded text-xs font-medium border border-red-800/80 transition"
                        title="Delete Paper"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Paper Detail Modal Preview */}
        {selectedPaper && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
            <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl">
              {/* Modal Header */}
              <div className="p-6 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white">{selectedPaper.title}</h3>
                  <div className="text-xs text-slate-400 flex items-center gap-3 mt-1 font-mono">
                    <span>ID: {selectedPaper.paper_id}</span>
                    <span>Total Marks: {selectedPaper.total_marks}</span>
                    <span>Questions: {selectedPaper.total_questions}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() =>
                      downloadFile(
                        `http://127.0.0.1:8011/api/v1/generated-papers/${selectedPaper.paper_id}/docx`,
                        `${selectedPaper.paper_id}.docx`
                      )
                    }
                    className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold"
                  >
                    📄 Word (.docx)
                  </button>
                  <button
                    onClick={() =>
                      downloadFile(
                        `http://127.0.0.1:8011/api/v1/generated-papers/${selectedPaper.paper_id}/pdf`,
                        `${selectedPaper.paper_id}_Exam.pdf`
                      )
                    }
                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold"
                  >
                    📥 Student PDF
                  </button>
                  <button
                    onClick={() =>
                      downloadFile(
                        `http://127.0.0.1:8011/api/v1/generated-papers/${selectedPaper.paper_id}/solutions-pdf`,
                        `${selectedPaper.paper_id}_Solutions.pdf`
                      )
                    }
                    className="px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-semibold"
                  >
                    🔑 Solutions PDF
                  </button>
                  <button
                    onClick={() => setSelectedPaper(null)}
                    className="p-2 text-slate-400 hover:text-white rounded-lg"
                  >
                    ✕
                  </button>
                </div>
              </div>

              {/* Modal Body */}
              <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-200">
                <div className="space-y-4">
                  {selectedPaper.questions?.map((q, idx) => (
                    <div
                      key={idx}
                      className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/80 space-y-2"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="font-semibold text-white">
                          <span className="text-blue-400 mr-2">Q{idx + 1}.</span>
                          {q.question}
                        </div>
                        <span className="bg-slate-700 text-slate-200 text-xs px-2.5 py-1 rounded-full font-bold whitespace-nowrap">
                          {q.marks} Mark{q.marks > 1 ? "s" : ""}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-2 text-xs text-slate-400 pt-1">
                        <span className="bg-slate-700/50 px-2 py-0.5 rounded">
                          Bloom: <strong className="text-slate-300">{q.bloom}</strong>
                        </span>
                        <span className="bg-slate-700/50 px-2 py-0.5 rounded">
                          Type: <strong className="text-slate-300">{q.question_type}</strong>
                        </span>
                        {q.unit_name && (
                          <span className="bg-slate-700/50 px-2 py-0.5 rounded">
                            Unit: <strong className="text-slate-300">{q.unit_name}</strong>
                          </span>
                        )}
                      </div>
                      {q.answer && (
                        <div className="mt-2 p-3 bg-emerald-950/30 border border-emerald-800/40 rounded-lg text-xs text-emerald-300 space-y-1">
                          <div className="font-semibold text-emerald-400">Model Answer / Solution:</div>
                          <p className="whitespace-pre-line">{q.answer}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
