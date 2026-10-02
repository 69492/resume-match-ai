export default function ScoreCard({ score }) {
  const value = Math.max(0, Math.min(100, score.overall_score));
  return (
    <section className="score-panel" aria-labelledby="score-heading">
      <div className="score-ring" style={{ "--score": `${value * 3.6}deg` }}>
        <div><strong>{value.toFixed(1)}%</strong><span>overall match</span></div>
      </div>
      <div className="score-copy">
        <span className="eyebrow">Deterministic match score</span>
        <h2 id="score-heading">{score.score_label}</h2>
        <p>Based on semantic alignment between the supplied resume and job description.</p>
        <div className="score-breakdown">
          <div><span>Required match</span><strong>{score.required_score.toFixed(1)}%</strong></div>
          <div><span>Preferred match</span><strong>{score.preferred_score.toFixed(1)}%</strong></div>
        </div>
      </div>
    </section>
  );
}
