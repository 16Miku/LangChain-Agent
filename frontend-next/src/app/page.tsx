import { redirect } from 'next/navigation';

// ============================================================
// Home Page - Redirect to Chat
// ============================================================

export default function HomePage() {
  redirect('/chat');
}
