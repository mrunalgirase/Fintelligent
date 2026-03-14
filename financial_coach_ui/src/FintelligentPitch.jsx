import { useState, useEffect } from "react";

const hooks = [
  {
    icon: "🔥",
    label: "STREAK CULTURE",
    title: "Make money habits feel like Duolingo",
    desc: "Daily savings streaks. Break it and the owl gets mad. Students are already wired for this dopamine loop — redirect it toward wealth.",
    color: "#FF6B35",
    stat: "89% of streak users return daily",
  },
  {
    icon: "📲",
    label: "MONEY FLEX CARDS",
    title: "Make saving as shareable as a Strava run",
    desc: "Auto-generated Instagram story cards. \"I saved ₹5K this month 💸\" — free marketing + identity signal. Your users become your ads.",
    color: "#00C896",
    stat: "3.2x more sign-ups from shared cards",
  },
  {
    icon: "😨",
    label: "BROKE FRIEND FOMO",
    title: "Show them where they rank",
    desc: "Anonymous peer benchmarking. \"Your college peers save ₹3,200/mo avg. You saved ₹600.\" FOMO does the selling. You just show the number.",
    color: "#7C3AED",
    stat: "FOMO converts 2x better than features",
  },
  {
    icon: "💸",
    label: "FIRST SALARY HOOK",
    title: "Own the most emotional financial moment",
    desc: "Position FinTelligent as the app every student opens the day they get their first stipend. Catch them at peak motivation = lifetime loyalty.",
    color: "#F59E0B",
    stat: "First 30 days = 70% retention predictor",
  },
  {
    icon: "🤖",
    label: "AI THAT ROASTS YOU",
    title: "Brutal. Funny. Viral.",
    desc: "\"Bro, you spent ₹2,400 on Zomato. That's a flight ticket.\" Gen Z shares things that make them laugh at themselves. This IS the marketing.",
    color: "#EC4899",
    stat: "Humor-first apps get 4x organic shares",
  },
];

export default function FintelligentPitch() {
  const [active, setActive] = useState(0);
  const [animating, setAnimating] = useState(false);

  useEffect(() => {
    const t = setInterval(() => {
      setAnimating(true);
      setTimeout(() => {
        setActive((p) => (p + 1) % hooks.length);
        setAnimating(false);
      }, 300);
    }, 3500);
    return () => clearInterval(t);
  }, []);

  const h = hooks[active];

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0A0A0F",
      fontFamily: "'Georgia', serif",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: "24px",
      position: "relative",
      overflow: "hidden",
    }}>
      {/* Background glow */}
      <div style={{
        position: "absolute",
        width: "600px",
        height: "600px",
        borderRadius: "50%",
        background: `radial-gradient(circle, ${h.color}18 0%, transparent 70%)`,
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        transition: "background 0.6s ease",
        pointerEvents: "none",
      }} />

      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: "48px", zIndex: 1 }}>
        <div style={{
          fontSize: "11px",
          letterSpacing: "4px",
          color: "#555",
          textTransform: "uppercase",
          marginBottom: "12px",
          fontFamily: "monospace",
        }}>Why students will actually pay</div>
        <div style={{
          fontSize: "clamp(28px, 5vw, 48px)",
          fontWeight: "700",
          color: "#fff",
          lineHeight: 1.1,
        }}>
          Fin<span style={{ color: h.color, transition: "color 0.4s" }}>telligent</span>
        </div>
        <div style={{ color: "#444", fontSize: "13px", marginTop: "8px", fontFamily: "monospace" }}>
          The Duolingo + Strava playbook — for money
        </div>
      </div>

      {/* Main card */}
      <div style={{
        width: "100%",
        maxWidth: "560px",
        background: "#111118",
        border: `1px solid ${h.color}44`,
        borderRadius: "20px",
        padding: "40px",
        zIndex: 1,
        opacity: animating ? 0 : 1,
        transform: animating ? "translateY(12px)" : "translateY(0)",
        transition: "all 0.3s ease",
        boxShadow: `0 0 60px ${h.color}22`,
      }}>
        <div style={{ display: "flex", alignItems: "flex-start", gap: "20px" }}>
          <div style={{
            fontSize: "48px",
            lineHeight: 1,
            filter: "drop-shadow(0 0 12px currentColor)",
          }}>{h.icon}</div>
          <div style={{ flex: 1 }}>
            <div style={{
              fontSize: "10px",
              letterSpacing: "3px",
              color: h.color,
              textTransform: "uppercase",
              marginBottom: "8px",
              fontFamily: "monospace",
            }}>{h.label}</div>
            <div style={{
              fontSize: "22px",
              fontWeight: "700",
              color: "#fff",
              lineHeight: 1.3,
              marginBottom: "16px",
            }}>{h.title}</div>
            <div style={{
              fontSize: "15px",
              color: "#888",
              lineHeight: 1.7,
              marginBottom: "24px",
            }}>{h.desc}</div>
            <div style={{
              background: `${h.color}15`,
              border: `1px solid ${h.color}33`,
              borderRadius: "10px",
              padding: "12px 16px",
              fontSize: "13px",
              color: h.color,
              fontFamily: "monospace",
            }}>📊 {h.stat}</div>
          </div>
        </div>
      </div>

      {/* Dots */}
      <div style={{ display: "flex", gap: "8px", marginTop: "32px", zIndex: 1 }}>
        {hooks.map((hk, i) => (
          <button
            key={i}
            onClick={() => { setActive(i); }}
            style={{
              width: i === active ? "28px" : "8px",
              height: "8px",
              borderRadius: "4px",
              background: i === active ? h.color : "#333",
              border: "none",
              cursor: "pointer",
              transition: "all 0.3s ease",
              padding: 0,
            }}
          />
        ))}
      </div>

      {/* Bottom CTA frame */}
      <div style={{
        marginTop: "48px",
        maxWidth: "560px",
        width: "100%",
        display: "grid",
        gridTemplateColumns: "1fr 1fr 1fr",
        gap: "12px",
        zIndex: 1,
      }}>
        {[
          { label: "Less than", value: "2 chai/day", sub: "pricing framing" },
          { label: "Target", value: "18–26 yrs", sub: "student + youth" },
          { label: "Hook moment", value: "1st salary", sub: "peak motivation" },
        ].map((c, i) => (
          <div key={i} style={{
            background: "#111118",
            border: "1px solid #222",
            borderRadius: "12px",
            padding: "16px",
            textAlign: "center",
          }}>
            <div style={{ fontSize: "10px", color: "#555", marginBottom: "6px", fontFamily: "monospace", letterSpacing: "1px" }}>{c.label}</div>
            <div style={{ fontSize: "16px", fontWeight: "700", color: "#fff" }}>{c.value}</div>
            <div style={{ fontSize: "10px", color: "#444", marginTop: "4px", fontFamily: "monospace" }}>{c.sub}</div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: "32px", color: "#333", fontSize: "11px", fontFamily: "monospace", zIndex: 1 }}>
        click dots to explore • auto-cycles every 3.5s
      </div>
    </div>
  );
}
