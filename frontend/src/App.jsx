import { useState } from "react";
import Header from "./components/Header";
import ResultsDashboard from "./components/ResultsDashboard";
import UploadCard from "./components/UploadCard";
import { analyzeResume } from "./services/api";

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const mockAnalysis = {
  score: { overall_score: 82.4, score_label: "Strong Match", required_score: 86, preferred_score: 68 },
  strong_matches: [
    { skill: "Python", similarity: 0.94, evidence: { text: "Developed machine learning models using Python", source_type: "resume_experience", page_number: 1, verified: true, confidence: 1, status: "verified" }, status: "verified" },
    { skill: "FastAPI", similarity: 0.88, evidence: { text: "Built REST APIs using FastAPI", source_type: "resume_project", page_number: 2, verified: true, confidence: 0.98, status: "verified" }, status: "verified" },
    { skill: "SQL", similarity: 0.84, evidence: { text: "Designed relational database queries", source_type: "resume_experience", page_number: 1, verified: true, confidence: 0.91, status: "verified" }, status: "verified" },
  ],
  partial_matches: [{ skill: "React", similarity: 0.62, evidence: { text: "Contributed to a web application interface", source_type: "resume_project", page_number: 2, verified: true, confidence: 0.78, status: "corrected" }, status: "corrected" }],
  missing_skills: [{ skill: "AWS", verified: true, status: "verified" }, { skill: "Docker", verified: true, status: "verified" }],
  relevant_projects: [{ project: "SmartSeat", evidence: { text: "SmartSeat project with Python, FastAPI, and database work", source_type: "resume_project", page_number: 2, verified: true, confidence: 0.96, status: "verified" }, status: "verified" }],
  recommendations: [{ text: "Learn basic AWS services to address the missing requirement.", grounded_in: "AWS is a missing JD requirement.", status: "verified" }, { text: "Highlight your FastAPI experience in the resume summary.", grounded_in: "FastAPI is a strong JD requirement.", status: "verified" }],
  summary: "The candidate shows strong backend, Python, and API alignment, with cloud experience as the clearest gap.", summary_status: "verified",
  validation_summary: { total_claims: 10, verified_claims: 8, corrected_claims: 1, rejected_claims: 1 },
};

function validateFile(file) {
  if (!file) return "Choose a PDF file to continue.";
  if (file.size === 0) return "That file is empty. Choose a different PDF.";
  if (file.size > MAX_FILE_SIZE) return "Files must be smaller than 10 MB.";
  if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) return "Only PDF files are supported.";
  return "";
}

export default function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [result, setResult] = useState(null);
  const [isDemo, setIsDemo] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function chooseFile(kind, file) {
    const message = validateFile(file);
    setError(message);
    if (message) return;
    if (kind === "resume") setResumeFile(file); else setJdFile(file);
    setResult(null); setIsDemo(false);
  }

  async function handleAnalyze() {
    if (!resumeFile || !jdFile) return;
    setLoading(true); setError(""); setResult(null); setIsDemo(false);
    try { setResult(await analyzeResume(resumeFile, jdFile)); }
    catch (err) { setError(err instanceof Error ? err.message : "Analysis failed. Please try again."); }
    finally { setLoading(false); }
  }

  return <div className="app-shell" id="top">
    <Header onPreview={() => { setResult(mockAnalysis); setIsDemo(true); setError(""); }} />
    <main className="page-content">
      <section className="hero" id="analyze"><div className="hero-kicker"><span className="live-dot" /> Evidence-first matching</div><h1>See how your resume<br /><em>meets the role.</em></h1><p>Upload your resume and a job description to get a clear, evidence-backed view of your alignment.</p></section>
      <section className="upload-grid" aria-label="Analysis documents"><UploadCard kind="resume" file={resumeFile} onFile={(file) => chooseFile("resume", file)} onRemove={() => setResumeFile(null)} disabled={loading} /><UploadCard kind="jd" file={jdFile} onFile={(file) => chooseFile("jd", file)} onRemove={() => setJdFile(null)} disabled={loading} /></section>
      {error && <div className="error-message" role="alert"><span>!</span><div><strong>We couldn't start the analysis</strong><p>{error}</p></div></div>}
      <div className="analyze-row"><button className="primary-button" onClick={handleAnalyze} disabled={!resumeFile || !jdFile || loading}>{loading ? <><span className="spinner" />Analyzing resume...</> : <>Analyze resume <span>→</span></>}</button><span className="privacy-note">Your documents stay in your workspace.</span></div>
      {loading && <div className="loading-card"><span className="spinner dark" /><div><strong>Analyzing resume...</strong><p>Extracting documents, comparing requirements, and verifying insights.</p></div></div>}
      {result && <ResultsDashboard result={result} demo={isDemo} />}
    </main>
    <footer><span>ResumeMatch AI</span><span>Deterministic scoring · Evidence-backed insights</span></footer>
  </div>;
}
