# Deployment Guide

## Prerequisites

1. **Supabase Account**: Sign up at [supabase.com](https://supabase.com)
2. **OpenAI API Key**: Get one from [platform.openai.com](https://platform.openai.com)
3. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)

## Step 1: Set Up Supabase

### 1.1 Create a New Project

1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Fill in project details and create

### 1.2 Enable pgvector Extension

1. Go to your project dashboard
2. Navigate to **Database** → **Extensions**
3. Search for `vector` and enable it

### 1.3 Run the Migration

1. Go to **SQL Editor**
2. Copy the contents of `supabase/migrations/001_initial_schema.sql`
3. Paste and run the SQL script

### 1.4 Get Your Credentials

Go to **Settings** → **API** and note:
- `Project URL` (NEXT_PUBLIC_SUPABASE_URL)
- `anon public` key (NEXT_PUBLIC_SUPABASE_ANON_KEY)
- `service_role` key (SUPABASE_SERVICE_ROLE_KEY) - **Keep this secret!**

## Step 2: Configure Environment Variables

### 2.1 Local Development

Create `.env.local` in the project root:

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key
```

### 2.2 Vercel Deployment

Add these as environment variables in your Vercel project:
1. Go to your Vercel project settings
2. Navigate to **Environment Variables**
3. Add all four variables from above

## Step 3: Install Dependencies

```bash
npm install
```

## Step 4: Seed the Database

After setting up Supabase and environment variables:

```bash
# Option 1: Using the API endpoint (recommended)
npm run dev  # Start the dev server
curl -X POST http://localhost:3000/api/seed

# Option 2: Using the script directly
npx ts-node scripts/seed-database.ts
```

This will:
- Generate embeddings for all example queries using OpenAI
- Store them in Supabase with pgvector
- Enable vector similarity search

## Step 5: Test Locally

```bash
npm run dev
```

Visit `http://localhost:3000` and try:
- "Ensure all rivalry games are scheduled on weekends and broadcast on ESPN"
- "Limit FOX to maximum 2 games in primetime slots"
- "Ensure Lakers have at least 2 rest days between back-to-back games"

## Step 6: Deploy to Vercel

### 6.1 Via CLI

```bash
npm install -g vercel
vercel login
vercel
```

### 6.2 Via GitHub

1. Push your code to GitHub
2. Go to [vercel.com/new](https://vercel.com/new)
3. Import your repository
4. Add environment variables
5. Deploy!

## Post-Deployment

### Verify the Deployment

1. Visit your Vercel deployment URL
2. Test the search functionality
3. Check the Supabase dashboard for query logs

### Seed Production Database

After deploying to Vercel:

```bash
curl -X POST https://your-app.vercel.app/api/seed
```

## Architecture Overview

### Three-Stage ML Pipeline

1. **Template Classification (Vector Search)**
   - User query → OpenAI embedding (text-embedding-3-small)
   - pgvector cosine similarity search in Supabase
   - Returns closest matching template with confidence score

2. **Parameter Extraction (LLM)**
   - GPT-4o-mini with JSON mode
   - Extracts structured parameters from natural language
   - Handles negations and edge cases

3. **Feasibility Warning (Rule-based)**
   - Validates extracted parameters
   - Checks for logical inconsistencies
   - Provides warnings and suggestions

## Troubleshooting

### "Missing env.OPENAI_API_KEY" Error

Make sure you've set the `OPENAI_API_KEY` in your `.env.local` file.

### "Vector search error" or RPC Error

1. Verify pgvector extension is enabled in Supabase
2. Ensure the migration script ran successfully
3. Check that your service role key is correct

### No Results from Search

The database needs to be seeded first. Run:

```bash
curl -X POST http://localhost:3000/api/seed
```

### Vercel Build Fails

1. Check all environment variables are set in Vercel
2. Ensure Node.js version is compatible (18.x or 20.x)
3. Check build logs for specific errors

## Monitoring

### Supabase Dashboard

Monitor:
- Database queries
- API usage
- Error logs

### Vercel Dashboard

Monitor:
- Deployment status
- Function logs
- Analytics

### OpenAI Dashboard

Monitor:
- API usage
- Token consumption
- Rate limits

## Cost Estimation

### OpenAI Costs

- **Embeddings** (text-embedding-3-small): $0.02 per 1M tokens
  - ~100 words per query = ~150 tokens
  - 1000 queries ≈ $0.003
  
- **GPT-4o-mini**: $0.150 per 1M input tokens, $0.600 per 1M output tokens
  - Per query: ~200 input + ~100 output tokens
  - 1000 queries ≈ $0.09

### Supabase Costs

- Free tier: 500MB database, 2GB bandwidth
- Pro tier ($25/month): 8GB database, 50GB bandwidth

### Vercel Costs

- Free tier: 100GB bandwidth
- Unlimited deployments

**Estimated monthly cost for 10,000 queries: ~$10-15**

## Security Best Practices

1. **Never commit `.env.local`** - It's in `.gitignore`
2. **Use service role key only server-side** - Never expose in client code
3. **Enable RLS policies** - Already configured in migration
4. **Rate limiting** - Consider adding rate limiting for production
5. **API key rotation** - Rotate keys regularly

## Next Steps

1. ✅ Deploy to production
2. ⚡ Add user authentication (Supabase Auth)
3. 📊 Implement analytics/logging
4. 🤖 Train XGBoost model for feasibility (future enhancement)
5. 🎨 Add more constraint templates
6. 🔍 Implement search history
7. 💾 Add constraint export functionality

## Support

For issues or questions:
1. Check the [Next.js documentation](https://nextjs.org/docs)
2. Review [Supabase docs](https://supabase.com/docs)
3. See [OpenAI API reference](https://platform.openai.com/docs)

