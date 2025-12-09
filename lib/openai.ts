import OpenAI from 'openai'

if (!process.env.OPENAI_API_KEY) {
  throw new Error('Missing env.OPENAI_API_KEY')
}

export const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

export async function generateEmbedding(text: string): Promise<number[]> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: text,
  })
  
  return response.data[0].embedding
}

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY
const OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
const DEFAULT_MODEL = "anthropic/claude-opus-4.5"

export async function extractParameters(query: string, templateType: number, model?: string) {
  const selectedModel = model || DEFAULT_MODEL
  if (!OPENROUTER_API_KEY) {
    throw new Error('Missing env.OPENROUTER_API_KEY')
  }

  const systemPrompt = `You are a sports scheduling constraint parameter extractor. Extract parameters from the user's query based on the template type.

Template 1: Game Scheduling
- min: minimum number of games (default: 1)
- max: maximum number of games (default: 999)
- teams: team group/category (e.g., "rivalry_games", "all_teams")
- rounds: round group (e.g., "weekend_rounds", "all_rounds")
- networks: network name (e.g., "ESPN", "FOX")
- venues: venue group (e.g., "all_venues", "outdoor_stadiums")

Template 2: Time Slot Constraints
- min: minimum games per time slot
- max: maximum games per time slot
- time_slots: time slot group (e.g., "primetime_slots")
- networks: network name

Template 3: Team-specific Constraints
- teams: specific team or team group
- min: minimum constraint value
- max: maximum constraint value
- condition: specific condition (e.g., "consecutive_home_games")

Handle negations: "don't", "no", "avoid" → set max=0

Return ONLY valid JSON with extracted parameters. Use null for missing values.`

  const response = await fetch(`${OPENROUTER_BASE_URL}/chat/completions`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'http://localhost',
    },
    body: JSON.stringify({
      model: selectedModel,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: `Query: "${query}"\nTemplate Type: ${templateType}` }
      ],
      response_format: { type: 'json_object' },
      temperature: 1.0,
    }),
  })

  const responseJson = await response.json()

  if (responseJson.error) {
    console.error('OpenRouter API error:', responseJson.error)
    throw new Error(`OpenRouter API error: ${responseJson.error.message || 'Unknown error'}`)
  }

  let content = responseJson.choices[0].message.content
  
  if (content) {
    content = content.trim()
    if (content.startsWith('```json')) {
      content = content.slice(7)
    } else if (content.startsWith('```')) {
      content = content.slice(3)
    }
    if (content.endsWith('```')) {
      content = content.slice(0, -3)
    }
    content = content.trim()
  }
  
  return content ? JSON.parse(content) : {}
}

