export default function EvidenceCard({ item }) {
  const evidence = item.evidence;
  return (
    <article className="evidence-card">
      <div className="evidence-top"><div><span className="eyebrow">{item.skill}</span><strong>{Math.round(item.similarity * 100)}% match</strong></div><span className={`status-pill ${item.status}`}>{item.status}</span></div>
      <blockquote>{evidence.text ? `“${evidence.text}”` : "No supporting evidence was verified."}</blockquote>
      <div className="source-line"><span>{evidence.verified ? "Verified against resume data" : "Evidence rejected"}</span>{evidence.page_number ? <span>Page {evidence.page_number}</span> : null}{evidence.source_type ? <span>{evidence.source_type.replaceAll("_", " ")}</span> : null}</div>
    </article>
  );
}
