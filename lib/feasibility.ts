export interface FeasibilityResult {
  feasible: boolean
  confidence: number
  warnings: string[]
  suggestions: string[]
}

export function checkFeasibility(
  templateId: number,
  params: Record<string, any>
): FeasibilityResult {
  const warnings: string[] = []
  const suggestions: string[] = []
  let confidence = 0.95

  // Basic validation rules
  const min = parseInt(params.min) || 0
  const max = parseInt(params.max) || 999

  // Rule 1: min > max is infeasible
  if (min > max) {
    warnings.push(`Minimum value (${min}) is greater than maximum value (${max})`)
    confidence = 0.1
    suggestions.push("Adjust min/max values so minimum is less than or equal to maximum")
  }

  // Rule 2: max = 0 indicates negation (don't schedule)
  if (max === 0) {
    confidence = 0.85
    suggestions.push("This is a negation constraint (avoiding certain schedules)")
  }

  // Rule 3: Very high minimum values might be infeasible
  if (min > 100) {
    warnings.push(`Minimum value (${min}) seems unusually high`)
    confidence = Math.max(0.5, confidence - 0.2)
    suggestions.push("Verify if this minimum value is realistic for your scheduling scenario")
  }

  // Rule 4: Template-specific checks
  if (templateId === 1) {
    // Game Scheduling
    if (!params.teams && !params.rounds) {
      warnings.push("No specific teams or rounds specified - constraint may be too broad")
      confidence = Math.max(0.7, confidence - 0.1)
    }
  }

  if (templateId === 2) {
    // Time Slot Constraints
    if (min > 10) {
      warnings.push("More than 10 games in a single time slot may cause scheduling conflicts")
      confidence = Math.max(0.6, confidence - 0.15)
      suggestions.push("Consider distributing games across multiple time slots")
    }
  }

  if (templateId === 3) {
    // Team-specific Constraints
    if (!params.teams) {
      warnings.push("No specific team mentioned - constraint may apply too broadly")
      confidence = Math.max(0.7, confidence - 0.1)
    }
  }

  // Rule 5: Network capacity checks
  if (params.networks) {
    const knownNetworks = ['ESPN', 'FOX', 'CBS', 'NBC', 'ABC', 'TNT']
    const normalizedNetwork = params.networks.toUpperCase()
    const isKnownNetwork = knownNetworks.some(n => 
      normalizedNetwork.includes(n)
    )
    
    if (!isKnownNetwork) {
      warnings.push(`Network "${params.networks}" may not be a standard broadcaster`)
      confidence = Math.max(0.75, confidence - 0.1)
    }
  }

  const feasible = confidence > 0.5 && warnings.length === 0

  return {
    feasible,
    confidence: Math.round(confidence * 100) / 100,
    warnings,
    suggestions: feasible && suggestions.length === 0 
      ? ["This constraint appears feasible and well-formed"]
      : suggestions
  }
}

