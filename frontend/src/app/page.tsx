export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-500 text-white">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" />
              </svg>
            </div>
            <span className="text-xl font-bold text-gray-900">DClaw Secure</span>
          </div>
          <div className="hidden items-center gap-8 md:flex">
            <a href="#features" className="text-sm font-medium text-gray-600 hover:text-gray-900">Features</a>
            <a href="#how-it-works" className="text-sm font-medium text-gray-600 hover:text-gray-900">How it works</a>
            <a href="#pricing" className="text-sm font-medium text-gray-600 hover:text-gray-900">Pricing</a>
          </div>
          <div className="flex items-center gap-3">
            <a
              href="/dashboard"
              className="rounded-lg px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100"
            >
              Sign in
            </a>
            <a
              href="/dashboard"
              className="rounded-lg bg-red-500 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-600"
            >
              Get started
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden pt-16 pb-24 sm:pt-24 sm:pb-32">
        <div className="absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-br from-red-50 via-white to-gray-50" />
          <div className="absolute top-0 right-0 h-[500px] w-[500px] rounded-full bg-red-100/40 blur-3xl" />
          <div className="absolute bottom-0 left-0 h-[400px] w-[400px] rounded-full bg-gray-100/60 blur-3xl" />
        </div>

        <div className="mx-auto max-w-7xl px-4 text-center sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-red-200 bg-red-50 px-4 py-1.5 text-sm font-medium text-red-700">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-red-500" />
              </span>
              Open-source security platform — deploy in 48 hours
            </div>
            <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl">
              Security posture,
              <span className="text-red-500"> unified.</span>
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Asset inventory, vulnerability management, security scanning, and compliance automation — in one AI-native platform. Built for startups that take security seriously.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <a
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-xl bg-red-500 px-8 py-4 text-base font-semibold text-white shadow-lg shadow-red-500/20 transition hover:bg-red-600 hover:shadow-red-500/30"
              >
                Launch dashboard
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
                </svg>
              </a>
              <a
                href="https://github.com/dclawstack/dclaw-secure"
                className="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-8 py-4 text-base font-semibold text-gray-700 transition hover:bg-gray-50"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
                </svg>
                View on GitHub
              </a>
            </div>
          </div>

          {/* Hero image / dashboard preview */}
          <div className="mx-auto mt-16 max-w-5xl">
            <div className="relative rounded-2xl border border-gray-200 bg-white p-2 shadow-2xl shadow-gray-200/50">
              <div className="overflow-hidden rounded-xl bg-gray-50">
                <div className="grid grid-cols-1 gap-6 p-6 md:grid-cols-3">
                  <div className="rounded-xl border border-gray-200 bg-white p-5">
                    <div className="mb-2 text-sm text-gray-500">Total Assets</div>
                    <div className="text-3xl font-bold text-gray-900">247</div>
                    <div className="mt-1 text-xs text-green-600">+12 this week</div>
                  </div>
                  <div className="rounded-xl border border-gray-200 bg-white p-5">
                    <div className="mb-2 text-sm text-gray-500">Vulnerabilities</div>
                    <div className="text-3xl font-bold text-red-600">18</div>
                    <div className="mt-1 text-xs text-gray-500">3 critical, 5 high</div>
                  </div>
                  <div className="rounded-xl border border-gray-200 bg-white p-5">
                    <div className="mb-2 text-sm text-gray-500">Compliance</div>
                    <div className="text-3xl font-bold text-blue-600">84%</div>
                    <div className="mt-1 text-xs text-blue-600">SOC2 on track</div>
                  </div>
                </div>
                <div className="border-t border-gray-200 bg-gray-50/50 px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="h-2.5 w-2.5 rounded-full bg-green-500" />
                    <span className="text-sm text-gray-600">Last scan completed 14 minutes ago</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trusted by / logos strip */}
      <section className="border-y bg-gray-50 py-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <p className="mb-6 text-center text-sm font-medium uppercase tracking-widest text-gray-400">
            Built for teams that ship fast and secure
          </p>
          <div className="flex flex-wrap items-center justify-center gap-8 opacity-60 grayscale">
            {["Y Combinator", "TechCrunch", "Product Hunt", "Hacker News", "AWS"].map((name) => (
              <span key={name} className="text-lg font-bold text-gray-700">{name}</span>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-16 text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Everything you need for security compliance
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              From asset inventory to AI-powered copilot — all in one open-source platform.
            </p>
          </div>

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: (
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
                  </svg>
                ),
                title: "Asset Inventory",
                desc: "Central registry of servers, containers, databases, APIs, and domains. Track risk scores, owners, and environments in one view.",
              },
              {
                icon: (
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                  </svg>
                ),
                title: "Vulnerability Management",
                desc: "Track CVEs, misconfigurations, and findings linked to assets. Severity scoring, status workflows, and remediation tracking.",
              },
              {
                icon: (
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75Z" />
                  </svg>
                ),
                title: "Security Scanning",
                desc: "Run vulnerability, container, API, and web scans against your assets. Real-time status, findings count, and risk scoring.",
              },
              {
                icon: (
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
                  </svg>
                ),
                title: "Real-time Dashboard",
                desc: "Unified security posture with total assets, open vulnerabilities, critical findings, recent scans, and environment breakdown.",
              },
              {
                icon: (
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 0 1-1.043 3.296 3.745 3.745 0 0 1-3.296 1.043A3.745 3.745 0 0 1 12 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 0 1-3.296-1.043 3.745 3.745 0 0 1-1.043-3.296A3.745 3.745 0 0 1 3 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 0 1 1.043-3.296 3.746 3.746 0 0 1 3.296-1.043A3.746 3.746 0 0 1 12 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 0 1 3.296 1.043 3.746 3.746 0 0 1 1.043 3.296A3.745 3.745 0 0 1 21 12Z" />
                  </svg>
                ),
                title: "Compliance Frameworks",
                desc: "Map controls to SOC2, ISO27001, and custom frameworks. Track implementation status, evidence, and audit readiness.",
              },
              {
                icon: (
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 3.75V16.5L12 14.25 7.5 16.5V3.75m9 0H18A2.25 2.25 0 0 1 20.25 6v12A2.25 2.25 0 0 1 18 20.25H6A2.25 2.25 0 0 1 3.75 18V6A2.25 2.25 0 0 1 6 3.75h1.5m9 0h-9" />
                  </svg>
                ),
                title: "Policy Management",
                desc: "Publish security policies, track employee acknowledgments, and measure compliance rates — the #1 pain point for auditors.",
              },
              {
                icon: (
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456Z" />
                  </svg>
                ),
                title: "AI Security Copilot",
                desc: "Ask natural language questions about your security posture. 'What are our top 5 critical vulnerabilities?' — powered by your real data.",
              },
              {
                icon: (
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 17.25v1.007a3 3 0 0 1-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0 1 15 18.257V17.25m6-12V15a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 15V5.25m18 0A2.25 2.25 0 0 0 18.75 3H5.25A2.25 2.25 0 0 0 3 5.25m18 0V12a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 12V5.25" />
                  </svg>
                ),
                title: "Self-hostable & Cloud",
                desc: "Docker + Helm charts for private deployments, or deploy to Vercel + AWS in minutes. Your data stays where you want it.",
              },
              {
                icon: (
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5" />
                  </svg>
                ),
                title: "Developer-First API",
                desc: "Fully typed REST API with OpenAPI spec, Pydantic schemas, and a typed TypeScript client. Build integrations in minutes.",
              },
            ].map((f) => (
              <div
                key={f.title}
                className="group rounded-2xl border border-gray-200 bg-white p-7 transition hover:border-red-200 hover:shadow-lg hover:shadow-red-500/5"
              >
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-red-50 text-red-600 transition group-hover:bg-red-500 group-hover:text-white">
                  {f.icon}
                </div>
                <h3 className="mb-2 text-lg font-semibold text-gray-900">{f.title}</h3>
                <p className="text-sm leading-relaxed text-gray-600">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="border-t bg-gray-50 py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-16 text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              How it works
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              From zero to full security visibility in three steps.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            {[
              {
                step: "01",
                title: "Register Assets",
                desc: "Add your servers, containers, databases, and APIs to the inventory. Assign owners, environments, and risk scores.",
              },
              {
                step: "02",
                title: "Run Scans & Track Vulns",
                desc: "Launch security scans, import CVE data, and manage findings through resolution workflows with severity tracking.",
              },
              {
                step: "03",
                title: "Monitor & Automate",
                desc: "Watch your real-time dashboard, map controls to compliance frameworks, and let the AI copilot answer your questions.",
              },
            ].map((s) => (
              <div key={s.step} className="relative rounded-2xl bg-white p-8 shadow-sm">
                <div className="mb-4 text-4xl font-black text-red-100">{s.step}</div>
                <h3 className="mb-2 text-xl font-semibold text-gray-900">{s.title}</h3>
                <p className="text-gray-600">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture / tech stack */}
      <section className="py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            <div>
              <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
                Built on a modern, scalable stack
              </h2>
              <p className="mt-4 text-lg text-gray-600">
                FastAPI + SQLAlchemy 2.0 on the backend. Next.js 14 + Tailwind on the frontend. PostgreSQL for data. Docker + Helm for deployment.
              </p>
              <div className="mt-8 grid grid-cols-2 gap-4">
                {[
                  ["FastAPI", "Async Python web framework"],
                  ["SQLAlchemy 2.0", "Modern ORM with async support"],
                  ["Next.js 14", "App Router + React Server Components"],
                  ["Tailwind CSS", "Utility-first styling"],
                  ["PostgreSQL", "Production-grade database"],
                  ["Docker + Helm", "Container & K8s deployment"],
                ].map(([name, desc]) => (
                  <div key={name} className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                    <div className="font-semibold text-gray-900">{name}</div>
                    <div className="text-sm text-gray-500">{desc}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-lg">
              <div className="space-y-4">
                <div className="flex items-center gap-3 rounded-lg bg-gray-50 p-3">
                  <div className="h-3 w-3 rounded-full bg-blue-500" />
                  <span className="text-sm font-medium text-gray-700">Backend API (FastAPI)</span>
                  <span className="ml-auto text-xs text-gray-400">Port 8031</span>
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-gray-50 p-3">
                  <div className="h-3 w-3 rounded-full bg-green-500" />
                  <span className="text-sm font-medium text-gray-700">Frontend (Next.js)</span>
                  <span className="ml-auto text-xs text-gray-400">Port 3031</span>
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-gray-50 p-3">
                  <div className="h-3 w-3 rounded-full bg-purple-500" />
                  <span className="text-sm font-medium text-gray-700">PostgreSQL</span>
                  <span className="ml-auto text-xs text-gray-400">dclaw_secure</span>
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-gray-50 p-3">
                  <div className="h-3 w-3 rounded-full bg-orange-500" />
                  <span className="text-sm font-medium text-gray-700">Alembic Migrations</span>
                  <span className="ml-auto text-xs text-gray-400">Auto-generated</span>
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-gray-50 p-3">
                  <div className="h-3 w-3 rounded-full bg-red-500" />
                  <span className="text-sm font-medium text-gray-700">Docker Compose / Helm</span>
                  <span className="ml-auto text-xs text-gray-400">Production ready</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing teaser */}
      <section id="pricing" className="border-t bg-gray-50 py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-16 text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Simple, transparent pricing
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Start free. Scale when you're ready. No hidden fees.
            </p>
          </div>

          <div className="mx-auto grid max-w-4xl gap-8 md:grid-cols-2">
            <div className="rounded-2xl border border-gray-200 bg-white p-8">
              <h3 className="text-lg font-semibold text-gray-900">Open Source</h3>
              <p className="mt-2 text-gray-600">Self-hosted. Full feature set. Community support.</p>
              <div className="mt-6 text-4xl font-bold text-gray-900">$0</div>
              <p className="text-sm text-gray-500">Forever free</p>
              <ul className="mt-6 space-y-3 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                  </svg>
                  Asset inventory (unlimited)
                </li>
                <li className="flex items-center gap-2">
                  <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                  </svg>
                  Vulnerability tracking
                </li>
                <li className="flex items-center gap-2">
                  <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                  </svg>
                  Security scans
                </li>
                <li className="flex items-center gap-2">
                  <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                  </svg>
                  Real-time dashboard
                </li>
                <li className="flex items-center gap-2">
                  <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                  </svg>
                  Docker + Helm charts
                </li>
              </ul>
              <a
                href="https://github.com/dclawstack/dclaw-secure"
                className="mt-8 block w-full rounded-lg border border-gray-200 py-3 text-center text-sm font-semibold text-gray-700 hover:bg-gray-50"
              >
                View on GitHub
              </a>
            </div>

            <div className="relative rounded-2xl border-2 border-red-500 bg-white p-8 shadow-lg shadow-red-500/10">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-red-500 px-3 py-1 text-xs font-semibold text-white">
                Coming soon
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Cloud Pro</h3>
              <p className="mt-2 text-gray-600">Managed hosting, SSO, audit logs, and priority support.</p>
              <div className="mt-6 text-4xl font-bold text-gray-900">$49<span className="text-lg font-normal text-gray-500">/mo</span></div>
              <p className="text-sm text-gray-500">per organization</p>
              <ul className="mt-6 space-y-3 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                  </svg>
                  Everything in Open Source
                </li>
                <li className="flex items-center gap-2">
                  <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                  </svg>
                  Managed cloud hosting
                </li>
                <li className="flex items-center gap-2">
                  <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                  </svg>
                  SSO & SAML
                </li>
                <li className="flex items-center gap-2">
                  <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                  </svg>
                  Audit logs & compliance reports
                </li>
                <li className="flex items-center gap-2">
                  <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                  </svg>
                  AI Copilot (unlimited queries)
                </li>
              </ul>
              <button
                disabled
                className="mt-8 block w-full rounded-lg bg-gray-100 py-3 text-center text-sm font-semibold text-gray-400 cursor-not-allowed"
              >
                Join waitlist
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-red-600 py-20">
        <div className="mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Ready to secure your infrastructure?
          </h2>
          <p className="mt-4 text-lg text-red-100">
            Deploy in minutes with Docker, or clone the repo and customize for your org.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <a
              href="/dashboard"
              className="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-4 text-base font-semibold text-red-600 shadow-lg transition hover:bg-gray-100"
            >
              Launch dashboard
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
              </svg>
            </a>
            <a
              href="https://github.com/dclawstack/dclaw-secure"
              className="inline-flex items-center gap-2 rounded-xl border border-red-400 px-8 py-4 text-base font-semibold text-white transition hover:bg-red-700"
            >
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
              </svg>
              Star on GitHub
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-8 md:grid-cols-4">
            <div>
              <div className="flex items-center gap-2">
                <div className="flex h-6 w-6 items-center justify-center rounded bg-red-500 text-white">
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" />
                  </svg>
                </div>
                <span className="font-bold text-gray-900">DClaw Secure</span>
              </div>
              <p className="mt-3 text-sm text-gray-500">
                Open-source security and compliance management for modern teams.
              </p>
            </div>
            <div>
              <h4 className="mb-3 text-sm font-semibold text-gray-900">Product</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="/dashboard" className="hover:text-gray-900">Dashboard</a></li>
                <li><a href="/assets" className="hover:text-gray-900">Assets</a></li>
                <li><a href="/vulnerabilities" className="hover:text-gray-900">Vulnerabilities</a></li>
                <li><a href="/scans" className="hover:text-gray-900">Scans</a></li>
              </ul>
            </div>
            <div>
              <h4 className="mb-3 text-sm font-semibold text-gray-900">Resources</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-gray-900">Documentation</a></li>
                <li><a href="#" className="hover:text-gray-900">API Reference</a></li>
                <li><a href="#" className="hover:text-gray-900">Docker Setup</a></li>
                <li><a href="#" className="hover:text-gray-900">Helm Charts</a></li>
              </ul>
            </div>
            <div>
              <h4 className="mb-3 text-sm font-semibold text-gray-900">Community</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-gray-900">GitHub</a></li>
                <li><a href="#" className="hover:text-gray-900">Discord</a></li>
                <li><a href="#" className="hover:text-gray-900">Contributing</a></li>
                <li><a href="#" className="hover:text-gray-900">Status</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-10 border-t pt-6 text-center text-sm text-gray-500">
            © {new Date().getFullYear()} DClaw Secure. Open source under MIT license.
          </div>
        </div>
      </footer>
    </main>
  )
}
