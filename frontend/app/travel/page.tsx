export default function TravelPage() {
  return (
    <div style={{ padding: "40px", maxWidth: "1200px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "2rem", fontWeight: 800, marginBottom: "20px" }}>Travel Dashboard</h1>
      <p style={{ color: "var(--color-text-secondary)", marginBottom: "40px" }}>
        Welcome to your travel planning dashboard.
      </p>
      
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "24px" }}>
        {/* Placeholder Card 1 */}
        <div className="glass-card" style={{ padding: "24px" }}>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "12px" }}>Upcoming Trips</h2>
          <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>No upcoming trips scheduled.</p>
        </div>
        
        {/* Placeholder Card 2 */}
        <div className="glass-card" style={{ padding: "24px" }}>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "12px" }}>Recent Destinations</h2>
          <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>You haven't visited anywhere recently.</p>
        </div>
      </div>
    </div>
  );
}
