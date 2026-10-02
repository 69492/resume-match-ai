export default function ValidationSummary({ summary }) {
  return <section className="validation-card"><div className="validation-heading"><span className="shield">✓</span><div><h3>Analysis verification</h3><p>AI-generated insights are checked against resume and job-description data.</p></div></div><div className="validation-stats"><div><strong>{summary.verified_claims}</strong><span>Verified</span></div><div><strong>{summary.corrected_claims}</strong><span>Corrected</span></div><div><strong>{summary.rejected_claims}</strong><span>Rejected</span></div></div></section>;
}
