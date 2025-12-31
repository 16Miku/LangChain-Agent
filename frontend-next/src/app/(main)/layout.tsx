'use client';

// ============================================================
// Main Layout - For Chat/Settings Pages (with Sidebar)
// ============================================================

import { AuthProvider } from '@/components/providers/AuthProvider';
import { Sidebar } from '@/components/sidebar';

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthProvider>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <main className="flex flex-1 flex-col overflow-hidden">{children}</main>
      </div>
    </AuthProvider>
  );
}
