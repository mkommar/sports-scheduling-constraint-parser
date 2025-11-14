/**
 * Type definitions for the Sports Scheduling Constraint Parser
 */

export interface ConstraintTemplate {
  id: number
  name: string
  description: string
  template: string
  exampleQueries: string[]
}

export interface ParsedParameters {
  min?: number
  max?: number
  teams?: string
  rounds?: string
  networks?: string
  venues?: string
  time_slots?: string
  condition?: string
  [key: string]: any
}

export interface FeasibilityResult {
  feasible: boolean
  confidence: number
  warnings: string[]
  suggestions: string[]
}

export interface ParseResult {
  templateId: number
  templateName: string
  confidence: number
  constraintSentence: string
  parameters: ParsedParameters
  feasibility: FeasibilityResult
  matchReason: string
  originalQuery?: string
}

export interface VectorSearchResult {
  id: number
  template_id: number
  content: string
  similarity: number
}

export interface EmbeddingVector {
  embedding: number[]
}

export interface SupabaseConstraintExample {
  id: number
  template_id: number
  content: string
  embedding: number[]
  created_at: string
}

