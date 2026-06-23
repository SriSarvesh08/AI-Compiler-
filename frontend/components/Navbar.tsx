"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import ThemeToggle from "./ThemeToggle";

interface MockUser {
  name: string;
  email: string;
  avatar: string;
}

export default function Navbar() {
  const pathname = usePathname();
  const [user, setUser] = useState<MockUser | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem("auth_token");
      if (token) {
        try {
          const stored = localStorage.getItem("mock_user");
          if (stored) {
            setUser(JSON.parse(stored));
          } else {
            fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/me`, {
              headers: { Authorization: `Bearer ${token}` }
            })
              .then(r => r.json())
              .then(data => {
                if (data.email) {
                  setUser(data);
                  localStorage.setItem("mock_user", JSON.stringify(data));
                }
              });
          }
        } catch {}
      } else {
        setUser(null);
      }
    };

    checkAuth();
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
    setMenuOpen(false);
    setUserMenuOpen(false);
  };

  const navLinks = [
    { href: "/", label: "Home" },
    { href: "/compiler", label: "Compiler" },
    { href: "/evaluation", label: "Evaluation" },
    { href: "/settings", label: "Settings" },
  ];

  const isActive = (href: string) =>
    href === "/" ? pathname === "/" : pathname.startsWith(href);

  return (
    <nav
      style={{
        position: "sticky",
        top: 0,
        zIndex: 100,
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        borderBottom: "1px solid var(--color-border)",
        background: "rgba(250, 251, 252, 0.85)",
      }}
      className="dark:border-[var(--color-dark-border)] dark:bg-[rgba(11,15,26,0.85)]"
    >
      <div
        style={{
          maxWidth: 1280,
          margin: "0 auto",
          padding: "0 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          height: 64,
        }}
      >
        {/* Logo - Hidden when logged in (Sidebar handles it) */}
        {!user ? (
          <Link href="/home" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 10,
                background: "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "white",
                fontWeight: 800,
                fontSize: "0.9rem",
                flexShrink: 0,
                boxShadow: "0 4px 12px rgba(99,102,241,0.4)",
              }}
            >
              AI
            </div>
            <span
              style={{
                fontWeight: 800,
                fontSize: "1.1rem",
                color: "var(--color-text-primary)",
                letterSpacing: "-0.02em",
              }}
            >
              Compiler
            </span>
            <span
              style={{
                fontSize: "0.6rem",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.06em",
                padding: "2px 7px",
                borderRadius: 5,
                background: "var(--color-accent-glow)",
                color: "var(--color-accent)",
                marginLeft: 2,
              }}
            >
              v0.2
            </span>
          </Link>
        ) : (
          <div style={{ flex: 1 }} /> // Spacer when logo is hidden
        )}

        {/* Desktop Nav Links - Hidden when logged in */}
        {!user && (
          <div
            style={{ display: "flex", alignItems: "center", gap: 4 }}
            className="nav-desktop"
          >
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                style={{
                  padding: "6px 14px",
                  borderRadius: 8,
                  textDecoration: "none",
                  fontSize: "0.9rem",
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
                {link.label}
              </Link>
            ))}
          </div>
        )}

        {/* Right Side Actions */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <ThemeToggle />

          {user ? (
            <div style={{ display: "flex", alignItems: "center" }}>
              {/* User profile dropdown removed because it's now in the sidebar */}
            </div>
          ) : (
            <div style={{ display: "flex", gap: 8 }}>
              <Link
                href="/login"
                style={{
                  padding: "8px 18px",
                  borderRadius: 9,
                  border: "1px solid var(--color-border)",
                  textDecoration: "none",
                  fontSize: "0.9rem",
                  fontWeight: 600,
                  color: "var(--color-text-primary)",
                  transition: "all 0.2s",
                }}
                className="dark:border-[var(--color-dark-border)]"
              >
                Log in
              </Link>
              <Link
                href="/register"
                style={{
                  padding: "8px 18px",
                  borderRadius: 9,
                  background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                  textDecoration: "none",
                  fontSize: "0.9rem",
                  fontWeight: 600,
                  color: "white",
                  boxShadow: "0 2px 10px rgba(99,102,241,0.35)",
                  transition: "all 0.2s",
                }}
              >
                Sign up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
