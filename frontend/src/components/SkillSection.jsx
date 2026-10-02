const icons = { strong: "✓", partial: "◐", missing: "×" };

export default function SkillSection({ title, tone, items }) {
  return (
    <section className="skill-section">
      <div className="section-heading"><span className={`status-icon ${tone}`}>{icons[tone]}</span><h3>{title}</h3><span className="count">{items.length}</span></div>
      {items.length ? <div className="skill-list">{items.map((item) => <div className="skill-chip" key={`${item.skill}-${item.status}`}><span>{item.skill}</span><em className={`status-pill ${item.status}`}>{item.status}</em></div>)}</div> : <p className="empty-copy">No items in this category.</p>}
    </section>
  );
}
