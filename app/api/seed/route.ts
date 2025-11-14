import { NextResponse } from 'next/server'
import { generateEmbedding } from '@/lib/openai'
import { createServerSupabaseClient } from '@/lib/supabase'
import { constraintTemplates } from '@/lib/templates'

export async function POST() {
  try {
    const supabase = createServerSupabaseClient()

    // Prepare all example queries with embeddings
    const embeddingPromises = constraintTemplates.flatMap(template =>
      template.exampleQueries.map(async (query) => {
        const embedding = await generateEmbedding(query)
        return {
          template_id: template.id,
          content: query,
          embedding,
        }
      })
    )

    const embeddings = await Promise.all(embeddingPromises)

    // Insert into Supabase
    const { error } = await supabase
      .from('constraint_examples')
      .upsert(embeddings, { onConflict: 'content' })

    if (error) {
      console.error('Seed error:', error)
      return NextResponse.json(
        { error: 'Failed to seed database', details: error.message },
        { status: 500 }
      )
    }

    return NextResponse.json({
      success: true,
      message: `Seeded ${embeddings.length} example queries`,
      count: embeddings.length,
    })

  } catch (error) {
    console.error('Seed error:', error)
    return NextResponse.json(
      { error: 'Failed to seed database', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}

