import { useEffect, useState } from "react"

import { api } from "@/lib/api"
import { useDomainStore } from "@/store/domainStore"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

function Dashboard() {
  const { domains, activeDomainId, setDomains, setActive } = useDomainStore()

  const [name, setName] = useState("")
  const [slug, setSlug] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const activeDomain = domains.find((domain) => domain.id === activeDomainId)

  async function loadDomains() {
    try {
      setError("")
      const response = await api.get("/domains")
      const loadedDomains = response.data

      setDomains(loadedDomains)

      // If no active brain is selected yet, select the first one.
      if (!activeDomainId && loadedDomains.length > 0) {
        setActive(loadedDomains[0].id)
      }
    } catch (err) {
      console.error(err)
      setError("Could not load domains. Make sure the backend is running.")
    }
  }

  useEffect(() => {
    loadDomains()
  }, [])

  async function createDomain(event) {
    event.preventDefault()

    if (!name.trim() || !slug.trim()) {
      setError("Please enter both a domain name and slug.")
      return
    }

    try {
      setLoading(true)
      setError("")

      const response = await api.post("/domains", {
        name: name.trim(),
        slug: slug.trim(),
      })

      const newDomain = response.data

      setName("")
      setSlug("")

      const updatedDomains = [...domains, newDomain]
      setDomains(updatedDomains)
      setActive(newDomain.id)
    } catch (err) {
      console.error(err)

      const detail = err.response?.data?.detail

      if (detail) {
        setError(detail)
      } else {
        setError("Could not create domain.")
      }
    } finally {
      setLoading(false)
    }
  }

  async function deleteDomain(domainId) {
    try {
      setError("")
      await api.delete(`/domains/${domainId}`)

      const remainingDomains = domains.filter((domain) => domain.id !== domainId)
      setDomains(remainingDomains)

      if (activeDomainId === domainId) {
        setActive(remainingDomains.length > 0 ? remainingDomains[0].id : null)
      }
    } catch (err) {
      console.error(err)
      setError("Could not delete domain.")
    }
  }

  return (
    <main className="min-h-screen bg-background p-8 text-foreground">
      <div className="mx-auto max-w-5xl space-y-8">
        <section className="space-y-2">
          <p className="text-sm text-muted-foreground">
            Multi-agent research platform powered by Cognee
          </p>

          <h1 className="text-4xl font-bold tracking-tight">
            AgentOS
          </h1>

          <p className="max-w-2xl text-muted-foreground">
            Create domain-scoped knowledge brains, switch between them, and later run agents inside the selected brain.
          </p>
        </section>

        <Card>
          <CardHeader>
            <CardTitle>Current Brain</CardTitle>
            <CardDescription>
              Every question will run inside the selected domain brain.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            {domains.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No domains yet. Create one below.
              </p>
            ) : (
              <Select
                value={activeDomainId ?? ""}
                onValueChange={(value) => setActive(value)}
              >
                <SelectTrigger className="w-full max-w-sm">
                  <SelectValue placeholder="Select a brain" />
                </SelectTrigger>

                <SelectContent>
                  {domains.map((domain) => (
                    <SelectItem key={domain.id} value={domain.id}>
                      {domain.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}

            {activeDomain && (
              <div className="rounded-md border p-4 text-sm">
                <p>
                  <span className="font-medium">Selected:</span>{" "}
                  {activeDomain.title}
                </p>
                <p className="text-muted-foreground">
                  Dataset: {activeDomain.dataset_name}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Create New Domain</CardTitle>
            <CardDescription>
              A domain becomes a separate Cognee dataset, like AI Safety, Tax Law, or DevOps.
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={createDomain} className="grid gap-4 md:grid-cols-3">
              <Input
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Domain name, e.g. AI Safety"
              />

              <Input
                value={slug}
                onChange={(event) => setSlug(event.target.value)}
                placeholder="Slug, e.g. ai-safety"
              />

              <Button type="submit" disabled={loading}>
                {loading ? "Creating..." : "Create Domain"}
              </Button>
            </form>

            {error && (
              <p className="mt-4 text-sm text-red-500">
                {error}
              </p>
            )}
          </CardContent>
        </Card>

        <section className="space-y-4">
          <div>
            <h2 className="text-2xl font-semibold">Your Knowledge Brains</h2>
            <p className="text-sm text-muted-foreground">
              These domains come from your FastAPI backend.
            </p>
          </div>

          {domains.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">
                  No domains created yet.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {domains.map((domain) => {
                const isActive = domain.id === activeDomainId

                return (
                  <Card key={domain.id} className={isActive ? "border-primary" : ""}>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between gap-2">
                        <span>{domain.title}</span>
                        {isActive && (
                          <span className="rounded-full bg-primary px-2 py-1 text-xs text-primary-foreground">
                            Active
                          </span>
                        )}
                      </CardTitle>

                      <CardDescription>
                        Slug: {domain.slug}
                      </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-4">
                      <p className="break-all rounded-md bg-muted p-3 text-xs text-muted-foreground">
                        {domain.dataset_name}
                      </p>

                      <div className="flex gap-2">
                        <Button
                          type="button"
                          variant="secondary"
                          onClick={() => setActive(domain.id)}
                        >
                          Set Active
                        </Button>

                        <Button
                          type="button"
                          variant="destructive"
                          onClick={() => deleteDomain(domain.id)}
                        >
                          Delete
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}
        </section>
      </div>
    </main>
  )
}

export default Dashboard