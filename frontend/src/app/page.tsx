import Link from "next/link";
import { Shield } from "lucide-react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 px-4">
      <Shield className="h-16 w-16 text-[#EF4444]" />
      <h1 className="text-4xl font-bold text-[#EF4444]">DClaw Secure</h1>
      <p className="text-lg text-muted-foreground">
        Threat detection & vulnerability scanning
      </p>
      <Link
        href="/dashboard"
        className="inline-flex items-center justify-center rounded-md bg-[#EF4444] px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-[#dc2626]"
      >
        Go to Dashboard
      </Link>
    </main>
  );
}
