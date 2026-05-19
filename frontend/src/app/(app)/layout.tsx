import "../globals.css";
import AppShell from "@/components/app-shell";
import CopilotWidget from "@/components/copilot-widget";

export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <AppShell>
      {children}
      <CopilotWidget />
    </AppShell>
  );
}
