"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, Loader2 } from "lucide-react"

interface SearchInputProps {
  onSearch: (query: string) => void
  loading?: boolean
}

export function SearchInput({ onSearch, loading }: SearchInputProps) {
  const [query, setQuery] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto">
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
    </form>
  )
}

