"use client"

import { useState } from "react"
import { Navbar } from "@/components/navbar"
import { SearchInput } from "@/components/search-input"
import { SearchResult } from "@/components/search-result"
import { AuthGate } from "@/components/auth/auth-gate"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Sparkles } from "lucide-react"

interface ParseResult {
  templateId: number
  templateName: string
  confidence: number
  constraintSentence: string
  parameters: Record<string, any>
  feasibility: {
    feasible: boolean
    confidence: number
    warnings: string[]
    suggestions: string[]
  }
  matchReason: string
  originalQuery?: string
}

export default function Home() {
  const [result, setResult] = useState<ParseResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (query: string, model: string) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/parse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, model }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to parse query')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const [currentModel, setCurrentModel] = useState("anthropic/claude-opus-4.5")

  const exampleQueries = [
    'Ensure all rivalry games are scheduled on weekends and broadcast on ESPN',
    'Limit FOX to maximum 2 games in primetime slots',
    'Ensure Lakers have at least 2 rest days between back-to-back games'
  ]

  const handleExampleClick = (query: string) => {
    handleSearch(query, currentModel)
  }

  return (
    <AuthGate>
      <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
        <Navbar />
        
        <main className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center space-y-6 mb-12">
          <div className="flex items-center justify-center space-x-2">
            <Sparkles className="h-8 w-8 text-primary" />
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
              Translate Natural Language to
            </h1>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-primary">
            Scheduling Constraints
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Powered by OpenAI embeddings, GPT-4o-mini, and pgvector for intelligent 
            constraint parsing and validation
          </p>
        </div>

        {/* Search Section */}
        <div className="mb-8">
          <SearchInput 
            onSearch={handleSearch} 
            onModelChange={setCurrentModel}
            loading={loading} 
          />
        </div>

        {/* Example Queries */}
        {!result && !loading && (
          <div className="text-center space-y-4 mb-12">
            <p className="text-sm text-muted-foreground">Try these examples:</p>
            <div className="flex flex-wrap gap-2 justify-center max-w-3xl mx-auto">
              {exampleQueries.map((query, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  size="sm"
                  onClick={() => handleExampleClick(query)}
                  className="text-xs"
                >
                  {query}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 text-center">
              <p className="text-destructive font-medium">{error}</p>
            </div>
          </div>
        )}

        {/* Results Section */}
        {result && <SearchResult result={result} />}

        {/* Feature Badges */}
        {!result && !loading && (
          <div className="mt-16 pt-8 border-t">
            <p className="text-center text-sm text-muted-foreground mb-4">
              Production-ready ML pipeline with:
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              <Badge variant="outline">Vector Search</Badge>
              <Badge variant="outline">LLM Parameter Extraction</Badge>
              <Badge variant="outline">Feasibility Validation</Badge>
              <Badge variant="outline">Supabase pgvector</Badge>
              <Badge variant="outline">OpenAI GPT-4o-mini</Badge>
              <Badge variant="outline">TypeScript Strict Mode</Badge>
            </div>
          </div>
        )}
      </main>
    </div>
    </AuthGate>
  )
}

