# Quick Setup Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites

- Node.js 18+ or 20+ installed
- npm or yarn package manager
- Git

### Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/mkommar/sports-scheduling-constraint-parser.git
cd sports-scheduling-constraint-parser

# Install dependencies
npm install
```

### Step 2: Set Up Supabase

1. **Create a Supabase account** at [supabase.com](https://supabase.com)

2. **Create a new project**:
   - Go to your Supabase dashboard
   - Click "New Project"
   - Fill in project name and password
   - Wait for project to initialize (~2 minutes)

3. **Enable pgvector extension**:
   - Go to **Database** → **Extensions** in your project
   - Search for "vector"
   - Enable the extension

4. **Run the database migration**:
   - Go to **SQL Editor**
   - Create a new query
   - Copy the entire contents of `supabase/migrations/001_initial_schema.sql`
   - Paste and click "Run"
   - You should see "Success. No rows returned"

5. **Get your API credentials**:
   - Go to **Settings** → **API**
   - Copy these three values:
     - `Project URL`
     - `anon public` key
     - `service_role` key (click to reveal)

### Step 3: Set Up OpenAI

1. **Get an OpenAI API key**:
   - Go to [platform.openai.com](https://platform.openai.com)
   - Sign up or log in
   - Go to **API Keys**
   - Click "Create new secret key"
   - Copy the key (you won't be able to see it again!)

### Step 4: Configure Environment Variables

1. **Copy the example file**:
```bash
cp .env.local.example .env.local
```

2. **Edit `.env.local`** with your credentials:
```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...

# OpenAI
OPENAI_API_KEY=sk-...
```

### Step 5: Seed the Database

Start the development server and seed the database with example queries:

```bash
# Terminal 1: Start the dev server
npm run dev

# Terminal 2: Seed the database
curl -X POST http://localhost:3000/api/seed
```

You should see:
```json
{
  "success": true,
  "message": "Seeded 15 example queries",
  "count": 15
}
```

### Step 6: Test the Application

1. **Open your browser** to `http://localhost:3000`

2. **Try an example query**:
   - Type: "Ensure all rivalry games are scheduled on weekends and broadcast on ESPN"
   - Click "Parse"
   - You should see results within 1-2 seconds

3. **Try the example buttons** below the search bar

## ✅ Verification Checklist

- [ ] Dependencies installed without errors
- [ ] Supabase project created
- [ ] pgvector extension enabled
- [ ] Database migration ran successfully
- [ ] OpenAI API key obtained
- [ ] `.env.local` file created with all 4 variables
- [ ] Development server starts (`npm run dev`)
- [ ] Database seeded (15 examples)
- [ ] Application loads in browser
- [ ] Can parse a query successfully

## 🐛 Troubleshooting

### "Module not found" errors

```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### "Missing env.OPENAI_API_KEY"

- Check that `.env.local` exists in the project root
- Check that the variable is spelled correctly
- Restart the dev server after adding env variables

### "Vector search error" or "RPC does not exist"

- Verify pgvector extension is enabled in Supabase
- Check that the SQL migration ran successfully
- Try re-running the migration SQL

### "No matching template found"

- The database needs to be seeded first
- Run: `curl -X POST http://localhost:3000/api/seed`
- Check Supabase → **Table Editor** → `constraint_examples` has rows

### Port 3000 already in use

```bash
# Kill the process using port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
npm run dev -- -p 3001
```

## 📖 Next Steps

### Local Development

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system
- See [TESTING.md](./TESTING.md) for testing guidelines
- Check [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment

### Customization

**Add your own constraint templates**:

1. Edit `lib/templates.ts`
2. Add a new template with example queries
3. Re-run the seed script: `curl -X POST http://localhost:3000/api/seed`

**Modify the UI**:

1. Components are in `components/`
2. Main page is `app/page.tsx`
3. Styles use Tailwind CSS classes

**Adjust the ML pipeline**:

1. Embeddings: `lib/openai.ts` → `generateEmbedding()`
2. Parameter extraction: `lib/openai.ts` → `extractParameters()`
3. Feasibility: `lib/feasibility.ts` → `checkFeasibility()`

## 🚢 Deploy to Production

See the comprehensive [DEPLOYMENT.md](./DEPLOYMENT.md) guide for:
- Deploying to Vercel
- Setting up production environment variables
- Seeding the production database
- Monitoring and cost estimation

Quick deploy button:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/mkommar/sports-scheduling-constraint-parser)

## 💡 Tips

### Development Workflow

1. **Make changes** to code
2. **Check browser** (hot reload is automatic)
3. **Check console** for errors
4. **Test manually** with different queries
5. **Check Supabase logs** if needed

### Cost Management (Development)

- **OpenAI free tier**: $5 credit for new accounts
- **Supabase free tier**: 500MB database, 2GB bandwidth
- **Development testing**: ~1000 queries = $0.10

### Useful Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint

# Seed database
curl -X POST http://localhost:3000/api/seed
```

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com)

## 🆘 Getting Help

1. **Check the docs**: [README.md](./README.md), [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **Common issues**: See troubleshooting section above
3. **Check logs**: Browser console, terminal, Supabase dashboard
4. **Open an issue**: Describe the problem with error messages and steps to reproduce

## 🎉 Success!

You're all set! Try these example queries to see the ML pipeline in action:

1. "Ensure all rivalry games are scheduled on weekends and broadcast on ESPN"
2. "Limit FOX to maximum 2 games in primetime slots"
3. "Ensure Lakers have at least 2 rest days between back-to-back games"
4. "Don't schedule more than 3 games on CBS in evening time slots"
5. "Schedule division games on FOX during weekend rounds"

Happy coding! 🚀

