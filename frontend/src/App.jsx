import { Button } from "@/components/ui/button"

function App() {
  return (
    <main className="min-h-screen bg-background p-8 text-foreground">
      <div className="mx-auto max-w-3xl space-y-4">
        <p className="text-sm text-muted-foreground">AgentOS frontend setup</p>

        <h1 className="text-3xl font-bold">
          AgentOS
        </h1>

        <p className="text-muted-foreground">
          Vite, React JavaScript, Tailwind, shadcn/ui, Axios, Zustand, and SWR are ready.
        </p>

        <Button>Frontend setup works</Button>
      </div>
    </main>
  )
}

export default App