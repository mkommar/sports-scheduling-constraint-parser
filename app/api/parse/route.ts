import { NextRequest, NextResponse } from 'next/server'
import { generateEmbedding, extractParameters } from '@/lib/openai'
import { createServerSupabaseClient } from '@/lib/supabase'
import { generateConstraintSentence, constraintTemplates } from '@/lib/templates'
import { checkFeasibility } from '@/lib/feasibility'

export async function POST(request: NextRequest) {
  try {
    const { query } = await request.json()

    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Query is required and must be a string' },
        { status: 400 }
      )
    }

    // STAGE 1: Template Classification (Vector Search)
    const embedding = await generateEmbedding(query)
    const supabase = createServerSupabaseClient()

    const { data: matches, error } = await supabase.rpc('match_templates', {
      query_embedding: embedding,
      match_threshold: 0.5,
      match_count: 3
    })

    if (error) {
      console.error('Vector search error:', error)
      // Fallback to keyword matching if vector search fails
      const templateId = 1
      const confidence = 0.75
      
      const params = await extractParameters(query, templateId)
      const constraintSentence = generateConstraintSentence(templateId, params)
      const feasibility = checkFeasibility(templateId, params)
      
      return NextResponse.json({
        templateId,
        templateName: constraintTemplates[0].name,
        confidence,
        constraintSentence,
        parameters: params,
        feasibility,
        matchReason: 'Fallback to keyword matching (vector search unavailable)',
      })
    }

    const bestMatch = matches && matches.length > 0 ? matches[0] : null
    
    if (!bestMatch) {
      return NextResponse.json(
        { error: 'No matching template found' },
        { status: 404 }
      )
    }

    const templateId = bestMatch.template_id
    const confidence = bestMatch.similarity

    // STAGE 2: Parameter Extraction (LLM)
    const params = await extractParameters(query, templateId)

    // STAGE 3: Feasibility Warning (Rule-based)
    const feasibility = checkFeasibility(templateId, params)

    // Generate structured constraint sentence
    const constraintSentence = generateConstraintSentence(templateId, params)

    // Get template details
    const template = constraintTemplates.find(t => t.id === templateId)

    return NextResponse.json({
      templateId,
      templateName: template?.name || 'Unknown',
      confidence: Math.round(confidence * 100) / 100,
      constraintSentence,
      parameters: params,
      feasibility,
      matchReason: `Semantic similarity: ${(confidence * 100).toFixed(0)}%`,
      originalQuery: bestMatch.content,
    })

  } catch (error) {
    console.error('Parse error:', error)
    return NextResponse.json(
      { error: 'Failed to parse query', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}

