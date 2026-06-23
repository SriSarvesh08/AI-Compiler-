"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

interface MockUser {
  name: string;
  email: string;
  avatar: string;
}

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<MockUser | null>(null);

  useEffect(() => {
    // Check auth state
    const checkAuth = () => {
      const token = localStorage.getItem("auth_token");
      if (token) {
        try {
          const stored = localStorage.getItem("mock_user");
          if (stored) setUser(JSON.parse(stored));
        } catch {}
      } else {
        setUser(null);
      }
    };

    checkAuth();
    // Re-check periodically or on storage events to catch logins from other components
    window.addEventListener("storage", checkAuth);
    const interval = setInterval(checkAuth, 1000);
    return () => {
      window.removeEventListener("storage", checkAuth);
      clearInterval(interval);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("mock_user");
    setUser(null);
    router.push("/");
  };

  if (!user) return null;

  const navLinks = [
    { href: "/compiler", label: "Compiler", icon: "M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" },
    { href: "/evaluation", label: "Evaluation", icon: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M16 13H8 M16 17H8 M10 9H8" },
    { href: "/settings", label: "Settings", icon: "M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z" },
  ];

  const isActive = (href: string) => pathname.startsWith(href);

  return (
    <aside
      style={{
        width: 260,
        height: "100vh",
        position: "sticky",
        top: 0,
        display: "flex",
        flexDirection: "column",
        borderRight: "1px solid var(--color-border)",
        background: "var(--color-bg-card)",
        zIndex: 200,
      }}
      className="dark:border-[var(--color-dark-border)] dark:bg-[var(--color-dark-bg-card)]"
    >
      {/* Brand Header */}
      <div style={{ padding: "24px", borderBottom: "1px solid var(--color-border)" }} className="dark:border-[var(--color-dark-border)]">
        <Link href="/home" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              background: "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontWeight: 800,
              fontSize: "0.85rem",
              flexShrink: 0,
              boxShadow: "0 4px 12px rgba(99,102,241,0.4)",
            }}
          >
            AI
          </div>
          <span
            style={{
              fontWeight: 800,
              fontSize: "1.05rem",
              color: "var(--color-text-primary)",
              letterSpacing: "-0.02em",
            }}
          >
            Compiler
          </span>
        </Link>
      </div>

      {/* Navigation Links */}
      <div style={{ flex: 1, padding: "24px 16px", display: "flex", flexDirection: "column", gap: 8 }}>
        <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--color-text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", paddingLeft: 12, marginBottom: 8 }}>
          Dashboard
        </div>
        
        {navLinks.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "10px 14px",
              borderRadius: 10,
              textDecoration: "none",
              fontSize: "0.92rem",
              fontWeight: isActive(link.href) ? 600 : 500,
              color: isActive(link.href)
                ? "var(--color-accent)"
                : "var(--color-text-secondary)",
              background: isActive(link.href)
                ? "var(--color-accent-glow)"
                : "transparent",
              transition: "all 0.2s",
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {link.icon.split(' M').map((path, i) => (
                <path key={i} d={(i > 0 ? 'M' : '') + path} />
              ))}
            </svg>
            {link.label}
          </Link>
        ))}
      </div>

      {/* User Profile & Logout Bottom Section */}
      <div style={{ padding: "20px 16px", borderTop: "1px solid var(--color-border)" }} className="dark:border-[var(--color-dark-border)]">
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16, padding: "0 8px" }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: "50%",
              background: "linear-gradient(135deg, #6366f1, #a855f7)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontWeight: 700,
              fontSize: "0.9rem",
              flexShrink: 0,
            }}
          >
            {user.name.charAt(0).toUpperCase()}
          </div>
          <div style={{ overflow: "hidden" }}>
            <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--color-text-primary)", whiteSpace: "nowrap", textOverflow: "ellipsis", overflow: "hidden" }}>
              {user.name}
            </div>
            <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", whiteSpace: "nowrap", textOverflow: "ellipsis", overflow: "hidden" }}>
              {user.email}
            </div>
          </div>
        </div>

        <button
          onClick={handleLogout}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 8,
            width: "100%",
            padding: "10px",
            borderRadius: 10,
            border: "1px solid var(--color-border)",
            background: "transparent",
            cursor: "pointer",
            fontSize: "0.85rem",
            fontWeight: 600,
            color: "var(--color-text-secondary)",
            transition: "all 0.2s",
          }}
          className="dark:border-[var(--color-dark-border)]"
          onMouseEnter={(e) => {
            e.currentTarget.style.color = "var(--color-error)";
            e.currentTarget.style.borderColor = "var(--color-error-bg)";
            e.currentTarget.style.background = "var(--color-error-bg)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = "var(--color-text-secondary)";
            e.currentTarget.style.borderColor = "var(--color-border)";
            e.currentTarget.style.background = "transparent";
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
          Sign out
        </button>
      </div>
    </aside>
  );
}
