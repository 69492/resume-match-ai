function formatSize(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export default function UploadCard({ kind, file, onFile, onRemove, disabled }) {
  const inputId = `${kind}-upload`;
  const isResume = kind === "resume";
  function handleChange(event) {
    onFile(event.target.files?.[0] || null);
    event.target.value = "";
  }
  return (
    <section className="upload-card">
      <div className={`upload-icon ${isResume ? "blue" : "violet"}`}>{isResume ? "↥" : "▤"}</div>
      <div className="upload-copy">
        <span className="eyebrow">{isResume ? "Candidate document" : "Role requirements"}</span>
        <h2>{isResume ? "Resume" : "Job description"}</h2>
        <p>{isResume ? "Upload your latest resume as a PDF." : "Upload the role description as a PDF."}</p>
      </div>
      {file ? (
        <div className="file-preview">
          <span className="file-badge">PDF</span>
          <span className="file-name" title={file.name}>{file.name}<small>{formatSize(file.size)}</small></span>
          <button className="icon-button" onClick={onRemove} disabled={disabled} aria-label={`Remove ${kind} file`}>×</button>
        </div>
      ) : (
        <label className="upload-button" htmlFor={inputId}>
          <span>Choose PDF</span>
          <input id={inputId} type="file" accept="application/pdf,.pdf" onChange={handleChange} disabled={disabled} />
        </label>
      )}
    </section>
  );
}
