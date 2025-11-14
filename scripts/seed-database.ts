/**
 * Database Seeding Script
 * 
 * This script seeds the Supabase database with example constraint queries
 * and their embeddings. Run this after setting up your Supabase project.
 * 
 * Usage:
 *   ts-node scripts/seed-database.ts
 * 
 * Or via API:
 *   curl -X POST http://localhost:3000/api/seed
 */

import { config } from 'dotenv'
import { resolve } from 'path'

// Load environment variables
config({ path: resolve(__dirname, '../.env.local') })

async function seedDatabase() {
  try {
    // Use the API endpoint to seed
    const response = await fetch('http://localhost:3000/api/seed', {
      method: 'POST',
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to seed database')
    }

    const result = await response.json()
    console.log('✅ Database seeded successfully!')
    console.log(`📊 Seeded ${result.count} example queries`)
  } catch (error) {
    console.error('❌ Error seeding database:', error)
    process.exit(1)
  }
}

if (require.main === module) {
  seedDatabase()
}

export { seedDatabase }

