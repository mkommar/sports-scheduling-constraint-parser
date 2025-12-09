"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, Loader2, Settings2 } from "lucide-react"

interface SearchInputProps {
  onSearch: (query: string, model: string) => void
  onModelChange?: (model: string) => void
  loading?: boolean
}

const DEFAULT_MODEL = "anthropic/claude-opus-4.5"

export function SearchInput({ onSearch, onModelChange, loading }: SearchInputProps) {
  const [query, setQuery] = useState("")
  const [model, setModel] = useState(DEFAULT_MODEL)
  const [showModelInput, setShowModelInput] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query, model)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto space-y-3">
      <div className="relative">
        <Input
          type="text"
          placeholder="e.g., Ensure all rivalry games are scheduled on weekends and broadcast on ESPN"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="h-14 pl-12 pr-32 text-base shadow-lg"
          disabled={loading}
        />
        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
        <Button
          type="submit"
          className="absolute right-2 top-1/2 transform -translate-y-1/2"
          disabled={loading || !query.trim()}
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Parsing...
            </>
          ) : (
            "Parse"
          )}
        </Button>
      </div>
      
      {/* Model Picker Toggle */}
      <div className="flex items-center justify-center gap-2">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => setShowModelInput(!showModelInput)}
          className="text-xs text-muted-foreground hover:text-foreground"
        >
          <Settings2 className="h-3 w-3 mr-1" />
          {showModelInput ? "Hide Model Settings" : "Change Model"}
        </Button>
        {!showModelInput && (
          <span className="text-xs text-muted-foreground">
            Using: <code className="bg-muted px-1 py-0.5 rounded">{model}</code>
          </span>
        )}
      </div>

      {/* Model Input */}
      {showModelInput && (
        <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg border">
          <label htmlFor="model-input" className="text-sm font-medium whitespace-nowrap">
            Model:
          </label>
          <Input
            id="model-input"
            type="text"
            placeholder="e.g., anthropic/claude-opus-4.5, openai/gpt-4o"
            value={model}
            onChange={(e) => {
              setModel(e.target.value)
              onModelChange?.(e.target.value)
            }}
            className="h-9 text-sm font-mono"
            disabled={loading}
          />
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => setModel(DEFAULT_MODEL)}
            className="whitespace-nowrap text-xs"
          >
            Reset
          </Button>
        </div>
      )}
    </form>
  )
}

