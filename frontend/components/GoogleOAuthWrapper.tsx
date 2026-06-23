"use client";

import { GoogleOAuthProvider } from "@react-oauth/google";

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

export default function GoogleOAuthWrapper({ children }: { children: React.ReactNode }) {
  if (!GOOGLE_CLIENT_ID) {
    // If no client ID is configured, just render children without provider
    return <>{children}</>;
  }
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      {children}
    </GoogleOAuthProvider>
  );
}
