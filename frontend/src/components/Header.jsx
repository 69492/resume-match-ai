export default function Header({ onPreview }) {
  return (
    <header className="topbar">
      <a className="brand" href="#top" aria-label="ResumeMatch AI home">
        <span className="brand-mark">R</span>
        <span><strong>ResumeMatch AI</strong><small>AI-Powered Career Intelligence</small></span>
      </a>
      <nav aria-label="Primary navigation">
        <a className="nav-link active" href="#analyze">Analyze</a>
        <button className="text-button" onClick={onPreview}>Preview sample</button>
      </nav>
    </header>
  );
}
