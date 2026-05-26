import type { FormEvent } from "react";

type AuthMode = "login" | "signup";

type AuthForm = {
  name: string;
  email: string;
  password: string;
};

export function AuthPanel({
  authMode,
  authForm,
  notice,
  setAuthMode,
  setAuthForm,
  submitAuth,
}: {
  authMode: AuthMode;
  authForm: AuthForm;
  notice: string;
  setAuthMode: (mode: AuthMode) => void;
  setAuthForm: (form: AuthForm | ((current: AuthForm) => AuthForm)) => void;
  submitAuth: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <main className="min-h-screen bg-slate-100 px-4 py-6 text-slate-950">
      <section className="mx-auto flex min-h-[calc(100vh-3rem)] w-full max-w-5xl items-center">
        <div className="grid w-full gap-4 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <p className="text-sm font-medium text-slate-500">Customer Support Analyzer</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-normal">
              Full-stack support review platform with an admin AI console
            </h1>
            <div className="mt-6 grid gap-3 text-sm text-slate-700 sm:grid-cols-2">
              <div className="rounded-md bg-slate-100 p-3">JWT auth and role-based access</div>
              <div className="rounded-md bg-slate-100 p-3">SQLite locally, PostgreSQL ready</div>
              <div className="rounded-md bg-slate-100 p-3">Customer review submission</div>
              <div className="rounded-md bg-slate-100 p-3">Admin RAG, ChromaDB, and PCA dashboard</div>
            </div>
          </div>

          <form onSubmit={submitAuth} className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="mb-5 flex rounded-md bg-slate-100 p-1">
              {(["login", "signup"] as const).map((mode) => (
                <button
                  key={mode}
                  className={`flex-1 rounded px-3 py-2 text-sm font-semibold ${
                    authMode === mode ? "bg-white text-slate-950" : "text-slate-600"
                  }`}
                  type="button"
                  onClick={() => setAuthMode(mode)}
                >
                  {mode === "login" ? "Login" : "Sign up"}
                </button>
              ))}
            </div>

            {authMode === "signup" && (
              <label className="mb-3 block text-sm font-medium">
                Name
                <input
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
                  value={authForm.name}
                  onChange={(event) =>
                    setAuthForm((current) => ({ ...current, name: event.target.value }))
                  }
                  required
                />
              </label>
            )}

            <label className="mb-3 block text-sm font-medium">
              Email
              <input
                className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
                type="email"
                value={authForm.email}
                onChange={(event) =>
                  setAuthForm((current) => ({ ...current, email: event.target.value }))
                }
                required
              />
            </label>

            <label className="mb-4 block text-sm font-medium">
              Password
              <input
                className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
                type="password"
                value={authForm.password}
                onChange={(event) =>
                  setAuthForm((current) => ({ ...current, password: event.target.value }))
                }
                required
              />
            </label>

            {notice && <p className="mb-3 text-sm text-red-700">{notice}</p>}

            <button className="w-full rounded-md bg-slate-900 px-4 py-3 text-sm font-semibold text-white">
              {authMode === "login" ? "Login" : "Create account"}
            </button>
            <p className="mt-3 text-xs text-slate-500">
              Demo admin: admin@example.com / admin123
            </p>
          </form>
        </div>
      </section>
    </main>
  );
}
