'use client';

// ============================================================
// Home Page - Redirect based on auth status
// ============================================================

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/stores';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isInitialized, initialize } = useAuthStore();

  useEffect(() => {
    // Initialize auth state on mount
    if (!isInitialized) {
      initialize();
      return;
    }

    // Redirect to appropriate page based on auth status
    if (isAuthenticated) {
      router.replace('/chat');
    } else {
      router.replace('/login');
    }
  }, [isAuthenticated, isInitialized, initialize, router]);

  // Show loading while checking auth
  return (
    <div className="flex h-screen w-screen items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    </div>
  );
}
