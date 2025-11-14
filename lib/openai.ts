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

export async function extractParameters(query: string, templateType: number) {
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

  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: `Query: "${query}"\nTemplate Type: ${templateType}` }
    ],
    response_format: { type: 'json_object' },
    temperature: 0.3,
  })

  const content = response.choices[0].message.content
  return content ? JSON.parse(content) : {}
}

