import EvidenceCard from "./EvidenceCard";
import ScoreCard from "./ScoreCard";
import SkillSection from "./SkillSection";
import ValidationSummary from "./ValidationSummary";

export default function ResultsDashboard({ result, demo = false }) {
  return <div className="results" id="results">
    <div className="results-title"><div><span className="eyebrow">{demo ? "Sample result" : "Your analysis"}</span><h2>Resume intelligence report</h2></div>{demo && <span className="demo-label">Preview only</span>}</div>
    <ScoreCard score={result.score} />
    <div className="skills-grid"><SkillSection title="Strong matches" tone="strong" items={result.strong_matches} /><SkillSection title="Partial matches" tone="partial" items={result.partial_matches} /><SkillSection title="Missing skills" tone="missing" items={result.missing_skills} /></div>
    <section className="content-section"><div className="section-heading"><span className="section-dot">✦</span><h3>Evidence</h3></div><div className="evidence-grid">{[...result.strong_matches, ...result.partial_matches].map((item) => <EvidenceCard item={item} key={`${item.skill}-${item.status}`} />)}</div></section>
    <div className="lower-grid">
      <section className="content-section"><div className="section-heading"><span className="section-dot">⌁</span><h3>Relevant projects</h3></div>{result.relevant_projects.length ? result.relevant_projects.map((item) => <article className="project-card" key={item.project}><div className="project-icon">◆</div><div><div className="project-title"><h4>{item.project}</h4><span className={`status-pill ${item.status}`}>{item.status}</span></div><p>{item.evidence.text || "Relevant project verified from resume data."}</p></div></article>) : <p className="empty-copy">No relevant projects were verified.</p>}</section>
      <section className="content-section"><div className="section-heading"><span className="section-dot">↗</span><h3>Recommendations</h3></div>{result.recommendations.length ? <ol className="recommendations">{result.recommendations.map((item) => <li key={item.text}><span>{item.text}</span>{item.status === "verified" && <small>{item.grounded_in}</small>}</li>)}</ol> : <p className="empty-copy">No recommendations available.</p>}</section>
    </div>
    <ValidationSummary summary={result.validation_summary} />
  </div>;
}
