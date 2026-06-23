import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Sidebar from "@/components/Sidebar";
import GoogleOAuthWrapper from "@/components/GoogleOAuthWrapper";
import Link from "next/link";

export const metadata: Metadata = {
  title: "AI Application Compiler",
  description:
    "Convert natural language software requirements into structured, validated application specifications using a multi-stage AI compiler pipeline.",
  keywords: "AI, compiler, application, schema, code generation, validation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;0,14..32,800;0,14..32,900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body style={{ margin: 0, minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        <GoogleOAuthWrapper>
          <div style={{ display: "flex", flex: 1 }}>
            <Sidebar />
            <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
              <Navbar />
              <main style={{ flex: 1 }}>{children}</main>
              <Footer />
            </div>
          </div>
        </GoogleOAuthWrapper>
      </body>
    </html>
  );
}

function Footer() {
  return (
    <footer
      style={{
        borderTop: "1px solid var(--color-border)",
        padding: "32px 24px",
        marginTop: "auto",
      }}
      className="dark:border-[var(--color-dark-border)]"
    >
      <div
        style={{
          maxWidth: 1280,
          margin: "0 auto",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 16,
        }}
      >
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontWeight: 800,
              fontSize: "0.72rem",
            }}
          >
            AI
          </div>
          <span style={{ fontWeight: 700, fontSize: "0.9rem" }}>AI Compiler</span>
          <span style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}>v0.2.0</span>
        </div>

        {/* Links */}
        <div style={{ display: "flex", gap: 24 }}>
          {[
            { href: "/", label: "Home" },
            { href: "/compiler", label: "Compiler" },
            { href: "/evaluation", label: "Evaluation" },
            { href: "/settings", label: "Settings" },
          ].map((link) => (
            <Link
              key={link.href}
              href={link.href}
              style={{
                fontSize: "0.82rem",
                color: "var(--color-text-muted)",
                textDecoration: "none",
                fontWeight: 500,
                transition: "color 0.2s",
              }}
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* Copyright */}
        <div style={{ fontSize: "0.78rem", color: "var(--color-text-muted)" }}>
          Runtime preview generated from validated configuration · Not a production system
        </div>
      </div>
    </footer>
  );
}
