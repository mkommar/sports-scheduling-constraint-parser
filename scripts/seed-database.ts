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

// Note: This script is designed to call the API endpoint
// Make sure your dev server is running: npm run dev

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
    console.error('💡 Make sure your dev server is running: npm run dev')
    process.exit(1)
  }
}

// Uncomment to run directly with ts-node:
// seedDatabase()

export { seedDatabase }

