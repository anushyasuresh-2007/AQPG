import React, { useState, useEffect } from "react";
import api, { getToken, formatApiError } from "../api";

const DIFFICULTY_PRESETS = {
  balanced: { easy: 30, medium: 50, hard: 20, label: "Balanced (30/50/20)" },
  rigorous: { easy: 20, medium: 40, hard: 40, label: "Rigorous / Board Exam (20/40/40)" },
  foundation: { easy: 50, medium: 40, hard: 10, label: "Foundation / Easy (50/40/10)" },
};

const BLOOM_PRESETS = {
  standard: {
    name: "Standard Academic",
    values: { Remember: 20, Understand: 20, Apply: 30, Analyze: 20, Evaluate: 10 },
  },
  application: {
    name: "Problem Solving & Numericals",
    values: { Remember: 10, Understand: 20, Apply: 40, Analyze: 20, Evaluate: 10 },
  },
  conceptual: {
    name: "Concept & Understanding",
    values: { Remember: 30, Understand: 40, Apply: 20, Analyze: 10, Evaluate: 0 },
  },
};

const ALL_QUESTION_TYPES = [
  "MCQ",
  "Very Short Answer",
  "Short Answer",
  "Long Answer",
  "Numerical",
  "Application Based",
  "Case Study",
  "Assertion Reason",
  "Problem Solving",
];

export default function GeneratePaper() {
  const [boards, setBoards] = useState([]);
  const [selectedBoard, setSelectedBoard] = useState("");
  const [selectedBoardObj, setSelectedBoardObj] = useState(null);

  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState("");
  const [selectedClassObj, setSelectedClassObj] = useState(null);

  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState("");
  const [selectedSubjectObj, setSelectedSubjectObj] = useState(null);

  const [units, setUnits] = useState([]);
  const [selectedUnits, setSelectedUnits] = useState([]);

  const [totalMarks, setTotalMarks] = useState(50);
  const [targetQuestionsCount, setTargetQuestionsCount] = useState(15);
  const [difficultyDistribution, setDifficultyDistribution] = useState(DIFFICULTY_PRESETS.balanced);
  const [selectedQuestionTypes, setSelectedQuestionTypes] = useState(ALL_QUESTION_TYPES);
  const [bloomDistribution, setBloomDistribution] = useState(BLOOM_PRESETS.standard.values);
  const [sourceMode, setSourceMode] = useState("hybrid");

  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [shortageDetails, setShortageDetails] = useState(null);
  const [generatedPaper, setGeneratedPaper] = useState(null);
  const [activeTab, setActiveTab] = useState("paper");

  // 1. Load Boards
  useEffect(() => {
    const fetchBoards = async () => {
      try {
        const res = await api.get("/boards");
        const bList = res.data || [];
        setBoards(bList);
        if (bList.length > 0) {
          setSelectedBoard(bList[0].code);
          setSelectedBoardObj(bList[0]);
        }
      } catch (err) {
        console.error("Failed to fetch boards", err);
      }
    };
    fetchBoards();
  }, []);

  // 2. Load Classes when Board changes
  useEffect(() => {
    if (!selectedBoardObj) return;
    const fetchClasses = async () => {
      try {
        const res = await api.get(`/classes?board_id=${selectedBoardObj.id}`);
        const classList = res.data || [];
        setClasses(classList);
        if (classList.length > 0) {
          const defClass = classList.find((c) => c.class_number === 10) || classList[0];
          setSelectedClass(defClass.class_code);
          setSelectedClassObj(defClass);
        } else {
          setSelectedClass("");
          setSelectedClassObj(null);
          setSubjects([]);
          setSelectedSubject("");
          setSelectedSubjectObj(null);
          setUnits([]);
          setSelectedUnits([]);
        }
      } catch (err) {
        console.error("Failed to fetch classes", err);
      }
    };
    fetchClasses();
  }, [selectedBoardObj]);

  // 3. Load Subjects when Board or Class changes
  useEffect(() => {
    if (!selectedBoardObj || !selectedClassObj) return;
    const fetchSubjects = async () => {
      try {
        const res = await api.get(`/subjects?board_id=${selectedBoardObj.id}&class_id=${selectedClassObj.id}`);
        const subList = res.data || [];
        setSubjects(subList);
        if (subList.length > 0) {
          setSelectedSubject(String(subList[0].id));
          setSelectedSubjectObj(subList[0]);
        } else {
          setSelectedSubject("");
          setSelectedSubjectObj(null);
          setUnits([]);
          setSelectedUnits([]);
        }
      } catch (err) {
        console.error("Failed to fetch subjects", err);
      }
    };
    fetchSubjects();
  }, [selectedBoardObj, selectedClassObj]);

  // 4. Load Units when Subject changes
  useEffect(() => {
    if (!selectedSubject) return;
    const fetchUnits = async () => {
      try {
        const res = await api.get(`/units?subject_id=${selectedSubject}`);
        const uList = res.data || [];
        setUnits(uList);
        setSelectedUnits(uList.map((u) => u.id));
      } catch (err) {
        console.error("Failed to fetch units", err);
      }
    };
    fetchUnits();
  }, [selectedSubject]);

  const handleBoardChange = (e) => {
    const bCode = e.target.value;
    setSelectedBoard(bCode);
    const bObj = boards.find((b) => b.code === bCode);
    setSelectedBoardObj(bObj || null);
  };

  const handleClassChange = (e) => {
    const cCode = e.target.value;
    setSelectedClass(cCode);
    const cObj = classes.find((c) => c.class_code === cCode);
    setSelectedClassObj(cObj || null);
  };

  const handleSubjectChange = (e) => {
    const sId = e.target.value;
    setSelectedSubject(sId);
    const sObj = subjects.find((s) => String(s.id) === sId);
    setSelectedSubjectObj(sObj || null);
  };

  const handleSelectAllUnits = () => {
    setSelectedUnits(units.map((u) => u.id));
  };

  const handleClearAllUnits = () => {
    setSelectedUnits([]);
  };

  const toggleUnit = (uId) => {
    setSelectedUnits((prev) =>
      prev.includes(uId) ? prev.filter((id) => id !== uId) : [...prev, uId]
    );
  };

  const toggleQuestionType = (t) => {
    setSelectedQuestionTypes((prev) =>
      prev.includes(t) ? prev.filter((item) => item !== t) : [...prev, t]
    );
  };

  const handleBloomChange = (level, val) => {
    const num = Math.max(0, Math.min(100, parseInt(val) || 0));
    setBloomDistribution((prev) => ({ ...prev, [level]: num }));
  };

  const applyBloomPreset = (presetKey) => {
    if (BLOOM_PRESETS[presetKey]) {
      setBloomDistribution(BLOOM_PRESETS[presetKey].values);
    }
  };

  const handleGenerate = async (overrideSourceMode = null) => {
    if (!selectedSubject) {
      setError("Please select a valid subject.");
      return;
    }

    const unitsToUse = selectedUnits.length > 0 ? selectedUnits : units.map((u) => u.id);

    const totalBloom = Object.values(bloomDistribution).reduce((a, b) => a + b, 0);
    if (totalBloom === 0) {
      setError("Bloom taxonomy distribution cannot be 0%");
      return;
    }

    const normalizedBloom = {};
    Object.entries(bloomDistribution).forEach(([k, v]) => {
      normalizedBloom[k] = Math.round((v / totalBloom) * 100);
    });

    const activeMode = overrideSourceMode || sourceMode;

    const { label, ...cleanDifficulty } = difficultyDistribution;

    const payload = {
      board: selectedBoardObj?.code || selectedBoard,
      class_name: selectedClassObj?.class_code || selectedClass,
      board_id: selectedBoardObj?.id,
      class_id: selectedClassObj?.id,
      subject_id: parseInt(selectedSubject),
      units: unitsToUse,
      total_marks: parseInt(totalMarks) || 50,
      number_of_questions: parseInt(targetQuestionsCount) || undefined,
      difficulty: "medium",
      difficulty_distribution: cleanDifficulty,
      bloom_distribution: normalizedBloom,
      question_types: selectedQuestionTypes,
      source_mode: activeMode,
      allow_ai_fallback: activeMode === "hybrid",
    };

    setGenerating(true);
    setError("");
    setShortageDetails(null);

    try {
      const res = await api.post("/generate-paper", payload);
      setGeneratedPaper(res.data);
      setActiveTab("paper");
    } catch (err) {
      const detail = formatApiError(err, "Question paper generation failed.");
      setError(detail);
      if (typeof detail === "string" && (detail.includes("insufficient approved questions") || detail.includes("Shortages:"))) {
        setShortageDetails(detail);
      }
    } finally {
      setGenerating(false);
    }
  };

  const downloadFile = (url, filename) => {
    const token = getToken();
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

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs rounded-full font-bold uppercase tracking-wider">
                Multi-Board AI Engine
              </span>
              <span className="px-2.5 py-1 bg-purple-500/10 text-purple-400 border border-purple-500/20 text-xs rounded-full font-bold uppercase tracking-wider">
                Hybrid Generation
              </span>
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 mt-2">
              ⚡ Automated AI Question Paper Generator
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Select Board, Class, and Subject to automatically load official curriculum units, balance marks, and assemble question papers.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <a
              href="/generated-papers"
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-sm font-semibold border border-slate-700 transition flex items-center gap-2"
            >
              📁 View Saved Papers
            </a>
          </div>
        </div>

        {/* Configuration & Output Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Configuration (5 Cols) */}
          <div className="lg:col-span-5 space-y-6">
            {/* Step 1: Dropdowns */}
            <div className="p-6 bg-slate-800/60 rounded-2xl border border-slate-700/80 shadow-xl space-y-4">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-extrabold">
                  1
                </span>
                Curriculum Hierarchy Selection
              </h2>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1 uppercase tracking-wider">
                  Educational Board
                </label>
                <select
                  value={selectedBoard}
                  onChange={handleBoardChange}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500 transition font-medium"
                >
                  {boards.map((b) => (
                    <option key={b.code} value={b.code}>
                      {b.name} ({b.code})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1 uppercase tracking-wider">
                  Academic Class / Grade
                </label>
                <select
                  value={selectedClass}
                  onChange={handleClassChange}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500 transition font-medium"
                >
                  {classes.map((c) => (
                    <option key={c.class_code} value={c.class_code}>
                      {c.class_code}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1 uppercase tracking-wider">
                  Subject
                </label>
                <select
                  value={selectedSubject}
                  onChange={handleSubjectChange}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500 transition font-medium"
                >
                  {subjects.map((s) => (
                    <option key={s.id} value={String(s.id)}>
                      {s.subject_name} {s.subject_code ? `(Code: ${s.subject_code})` : ""}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Step 2: Units Checkboxes */}
            <div className="p-6 bg-slate-800/60 rounded-2xl border border-slate-700/80 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs flex items-center justify-center font-extrabold">
                    2
                  </span>
                  Units / Chapters ({selectedUnits.length}/{units.length})
                </h2>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleSelectAllUnits}
                    className="text-xs text-blue-400 hover:text-blue-300 font-semibold px-2 py-1 bg-blue-950/60 rounded border border-blue-800/60"
                  >
                    Select All
                  </button>
                  <button
                    onClick={handleClearAllUnits}
                    className="text-xs text-slate-400 hover:text-slate-300 font-semibold px-2 py-1 bg-slate-700 rounded"
                  >
                    Clear
                  </button>
                </div>
              </div>

              {units.length === 0 ? (
                <div className="p-4 bg-slate-900 rounded-xl text-center text-slate-500 text-xs">
                  No syllabus units found for this subject. Ingest syllabus via Curriculum page.
                </div>
              ) : (
                <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                  {units.map((u) => (
                    <label
                      key={u.id}
                      className={`flex items-start gap-3 p-2.5 rounded-xl border transition cursor-pointer text-xs ${
                        selectedUnits.includes(u.id)
                          ? "bg-blue-950/40 border-blue-600/80 text-blue-200 font-medium"
                          : "bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700"
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedUnits.includes(u.id)}
                        onChange={() => toggleUnit(u.id)}
                        className="mt-0.5 rounded text-blue-600 focus:ring-0"
                      />
                      <span>{u.unit_name}</span>
                    </label>
                  ))}
                </div>
              )}
            </div>

            {/* Step 3: Paper Specs */}
            <div className="p-6 bg-slate-800/60 rounded-2xl border border-slate-700/80 shadow-xl space-y-4">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-purple-600 text-white text-xs flex items-center justify-center font-extrabold">
                  3
                </span>
                Paper Configuration
              </h2>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Total Marks
                  </label>
                  <input
                    type="number"
                    value={totalMarks}
                    onChange={(e) => setTotalMarks(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 font-bold focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Target Questions
                  </label>
                  <input
                    type="number"
                    value={targetQuestionsCount}
                    onChange={(e) => setTargetQuestionsCount(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 font-bold focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Question Types */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-2">
                  Question Types
                </label>
                <div className="flex flex-wrap gap-1.5">
                  {ALL_QUESTION_TYPES.map((t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => toggleQuestionType(t)}
                      className={`text-xs px-2.5 py-1 rounded-lg border transition ${
                        selectedQuestionTypes.includes(t)
                          ? "bg-indigo-600/80 border-indigo-500 text-white font-medium shadow-sm"
                          : "bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700"
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              {/* Bloom Distribution */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-semibold text-slate-300">
                    Bloom Taxonomy Distribution
                  </label>
                  <div className="flex gap-1">
                    {Object.keys(BLOOM_PRESETS).map((pKey) => (
                      <button
                        key={pKey}
                        type="button"
                        onClick={() => applyBloomPreset(pKey)}
                        className="text-[10px] text-slate-400 hover:text-blue-300 px-1.5 py-0.5 bg-slate-900 rounded border border-slate-800"
                      >
                        {BLOOM_PRESETS[pKey].name.split(" ")[0]}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {Object.entries(bloomDistribution).map(([lvl, val]) => (
                    <div key={lvl} className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                      <div className="text-[10px] text-slate-400 uppercase font-semibold">{lvl}</div>
                      <div className="flex items-center gap-1 mt-1">
                        <input
                          type="number"
                          value={val}
                          onChange={(e) => handleBloomChange(lvl, e.target.value)}
                          className="w-full bg-transparent text-sm font-bold text-white focus:outline-none"
                        />
                        <span className="text-xs text-slate-500">%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Question Source Selection */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-2">
                  Question Source Mode
                </label>
                <div className="space-y-2 text-xs">
                  <label
                    className={`flex items-start gap-2.5 p-2.5 rounded-xl border cursor-pointer transition ${
                      sourceMode === "hybrid"
                        ? "bg-purple-950/40 border-purple-600/80 text-purple-200"
                        : "bg-slate-900 border-slate-800 text-slate-400"
                    }`}
                  >
                    <input
                      type="radio"
                      name="source_mode"
                      value="hybrid"
                      checked={sourceMode === "hybrid"}
                      onChange={() => setSourceMode("hybrid")}
                      className="mt-0.5"
                    />
                    <div>
                      <div className="font-bold text-white flex items-center gap-1.5">
                        🤖 Hybrid Mode <span className="bg-purple-500/20 text-purple-300 px-1.5 py-0.2 rounded text-[10px]">Recommended</span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        Uses Question Bank first. AI automatically synthesizes missing questions.
                      </p>
                    </div>
                  </label>

                  <label
                    className={`flex items-start gap-2.5 p-2.5 rounded-xl border cursor-pointer transition ${
                      sourceMode === "bank"
                        ? "bg-blue-950/40 border-blue-600/80 text-blue-200"
                        : "bg-slate-900 border-slate-800 text-slate-400"
                    }`}
                  >
                    <input
                      type="radio"
                      name="source_mode"
                      value="bank"
                      checked={sourceMode === "bank"}
                      onChange={() => setSourceMode("bank")}
                      className="mt-0.5"
                    />
                    <div>
                      <div className="font-bold text-white">📚 Question Bank Only</div>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        Selects strictly from existing approved database questions.
                      </p>
                    </div>
                  </label>
                </div>
              </div>

              {/* Generate Action Button */}
              <button
                type="button"
                disabled={generating}
                onClick={() => handleGenerate()}
                className="w-full py-3.5 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 text-white font-extrabold rounded-xl shadow-lg shadow-blue-500/25 transition flex items-center justify-center gap-2 text-sm disabled:opacity-50"
              >
                {generating ? (
                  <>
                    <span className="inline-block animate-spin">⏳</span>
                    Synthesizing Question Paper...
                  </>
                ) : (
                  <>⚡ GENERATE QUESTION PAPER</>
                )}
              </button>
            </div>
          </div>

          {/* Right Column: Output / Result (7 Cols) */}
          <div className="lg:col-span-7 space-y-6">
            {error && (
              <div className="p-4 bg-red-950/60 border border-red-800 rounded-2xl text-red-300 text-sm space-y-3">
                <div className="flex items-center gap-2 font-bold text-red-200">
                  <span>⚠️</span> {String(error)}
                </div>
                {shortageDetails && (
                  <div className="pt-2 border-t border-red-900/60">
                    <p className="text-xs text-red-400 mb-2">
                      Would you like the AI Question Generator to automatically fill the missing questions?
                    </p>
                    <button
                      onClick={() => handleGenerate("hybrid")}
                      className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-lg text-xs font-bold shadow transition"
                    >
                      🤖 Generate Missing Questions with AI
                    </button>
                  </div>
                )}
              </div>
            )}

            {!generatedPaper && !generating && !error && (
              <div className="p-12 text-center bg-slate-800/40 rounded-2xl border border-slate-800 space-y-4">
                <div className="text-5xl">📄</div>
                <h3 className="text-xl font-bold text-slate-200">Ready to Assemble Examination</h3>
                <p className="text-slate-400 text-sm max-w-md mx-auto">
                  Configure your board curriculum parameters on the left and click <strong>Generate Question Paper</strong>.
                </p>
              </div>
            )}

            {generating && (
              <div className="p-16 text-center bg-slate-800/40 rounded-2xl border border-slate-800 space-y-4">
                <div className="inline-block animate-spin text-4xl">⚙️</div>
                <h3 className="text-xl font-bold text-slate-200">Synthesizing Pedagogical Exam Paper</h3>
                <p className="text-slate-400 text-sm max-w-md mx-auto">
                  Balancing Bloom taxonomy cognitive distribution, querying question bank, and applying subject-specific problem solving logic...
                </p>
              </div>
            )}

            {generatedPaper && (
              <div className="space-y-4">
                {/* Paper Controls Bar */}
                <div className="p-4 bg-slate-800/80 rounded-2xl border border-slate-700 flex flex-wrap items-center justify-between gap-3 shadow-xl">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setActiveTab("paper")}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                        activeTab === "paper"
                          ? "bg-blue-600 text-white shadow"
                          : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                      }`}
                    >
                      📄 Question Paper
                    </button>
                    <button
                      onClick={() => setActiveTab("blueprint")}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                        activeTab === "blueprint"
                          ? "bg-purple-600 text-white shadow"
                          : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                      }`}
                    >
                      📊 Blueprint Breakdown
                    </button>
                  </div>

                  {/* Export Options */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() =>
                        downloadFile(
                          `http://127.0.0.1:8011/api/v1/generated-papers/${generatedPaper.paper_id}/docx`,
                          `${generatedPaper.paper_id}.docx`
                        )
                      }
                      className="px-3 py-1.5 bg-blue-700 hover:bg-blue-600 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5"
                    >
                      📄 Word (.docx)
                    </button>
                    <button
                      onClick={() =>
                        downloadFile(
                          `http://127.0.0.1:8011/api/v1/generated-papers/${generatedPaper.paper_id}/pdf`,
                          `${generatedPaper.paper_id}_Exam.pdf`
                        )
                      }
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5"
                    >
                      📥 Student PDF
                    </button>
                    <button
                      onClick={() =>
                        downloadFile(
                          `http://127.0.0.1:8011/api/v1/generated-papers/${generatedPaper.paper_id}/solutions-pdf`,
                          `${generatedPaper.paper_id}_Solutions.pdf`
                        )
                      }
                      className="px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5"
                    >
                      🔑 Solutions PDF
                    </button>
                  </div>
                </div>

                {/* Printable Question Paper View */}
                {activeTab === "paper" && (
                  <div className="p-8 bg-white text-slate-900 rounded-2xl shadow-2xl space-y-6 font-sans">
                    {/* Header */}
                    <div className="text-center border-b-2 border-slate-900 pb-4 space-y-1">
                      <h2 className="text-2xl font-extrabold uppercase tracking-wide">
                        {generatedPaper.board || selectedBoard} EXAMINATION
                      </h2>
                      <h3 className="text-base font-bold text-slate-700">
                        {generatedPaper.class_name || selectedClass} · SUBJECT: {generatedPaper.subject_name || "Science"}
                      </h3>
                      {generatedPaper.unit_names && (
                        <p className="text-xs text-slate-500 italic">
                          Units Covered: {generatedPaper.unit_names}
                        </p>
                      )}
                      <div className="flex justify-between items-center text-xs font-bold pt-3">
                        <span>TIME ALLOWED: 3 HOURS</span>
                        <span>MAXIMUM MARKS: {generatedPaper.total_marks}</span>
                      </div>
                    </div>

                    {/* General Instructions */}
                    <div className="text-xs text-slate-600 space-y-1 border-b border-slate-300 pb-3">
                      <div className="font-bold text-slate-800">General Instructions:</div>
                      <ul className="list-disc pl-4 space-y-0.5 text-[11px]">
                        <li>All questions are compulsory.</li>
                        <li>Marks are indicated against each question.</li>
                        <li>Write clear, legible, step-by-step mathematical calculations where applicable.</li>
                      </ul>
                    </div>

                    {/* Questions List */}
                    <div className="space-y-4 text-sm text-slate-800">
                      {generatedPaper.questions && generatedPaper.questions.map((q, idx) => (
                        <div key={idx} className="space-y-1 border-b border-slate-100 pb-3">
                          <div className="flex justify-between items-start gap-4">
                            <div>
                              <span className="font-bold text-slate-900 mr-2">Q{idx + 1}.</span>
                              <span>{q.question}</span>
                            </div>
                            <span className="font-bold text-slate-900 whitespace-nowrap text-xs">
                              [{q.marks} Mark{q.marks > 1 ? "s" : ""}]
                            </span>
                          </div>
                          <div className="text-[10px] text-slate-400 flex items-center gap-2">
                            <span>Bloom: {q.bloom}</span>
                            <span>·</span>
                            <span>Type: {q.question_type}</span>
                            {q.unit_name && (
                              <>
                                <span>·</span>
                                <span>Unit: {q.unit_name}</span>
                              </>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="text-center font-bold text-xs pt-4 border-t-2 border-slate-900">
                      --- END OF QUESTION PAPER ---
                    </div>
                  </div>
                )}

                {/* Blueprint Breakdown Table */}
                {activeTab === "blueprint" && (
                  <div className="p-6 bg-slate-800/80 rounded-2xl border border-slate-700 shadow-xl space-y-4">
                    <h3 className="text-lg font-bold text-white">
                      📊 Exam Blueprint & Cognitive Distribution
                    </h3>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-sm text-slate-300">
                        <thead className="bg-slate-800 text-slate-400 text-xs uppercase font-semibold border-b border-slate-700">
                          <tr>
                            <th className="p-3">Cognitive Level</th>
                            <th className="p-3 text-center">Required %</th>
                            <th className="p-3 text-center">Target Marks</th>
                            <th className="p-3 text-center">Generated Marks</th>
                            <th className="p-3 text-center">Questions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700">
                          {generatedPaper.blueprint_summary && generatedPaper.blueprint_summary.map((b, i) => (
                            <tr key={i} className="hover:bg-slate-700/40">
                              <td className="p-3 font-semibold text-white">{b.bloom}</td>
                              <td className="p-3 text-center">{b.required_percentage}%</td>
                              <td className="p-3 text-center text-slate-400">{b.required_marks}</td>
                              <td className="p-3 text-center font-bold text-emerald-400">
                                {b.generated_marks}
                              </td>
                              <td className="p-3 text-center font-medium text-slate-200">
                                {b.generated_questions}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                        <tfoot className="bg-slate-800/80 font-bold text-white border-t border-slate-700">
                          <tr>
                            <td className="p-3">Total</td>
                            <td className="p-3 text-center">100%</td>
                            <td className="p-3 text-center">{generatedPaper.total_marks}</td>
                            <td className="p-3 text-center text-emerald-400">
                              {generatedPaper.total_marks}
                            </td>
                            <td className="p-3 text-center text-slate-200">
                              {generatedPaper.total_questions}
                            </td>
                          </tr>
                        </tfoot>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}