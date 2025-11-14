# Sports Scheduling Constraint Parser

A production-quality Next.js 14 application that translates natural language sports scheduling queries into structured constraints using a three-stage ML pipeline.

![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat&logo=next.js&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat&logo=supabase&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)

## 🎯 Overview

Built for the Fastbreak.ai ML Engineer role challenge, this application demonstrates:
- **Production-grade ML engineering** with vector search and LLM integration
- **Type-safe development** with TypeScript strict mode
- **Modern UI/UX** with shadcn/ui and Tailwind CSS
- **Scalable architecture** ready for Vercel deployment

## 🏗️ Architecture

### Three-Stage ML Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                      User Input Query                        │
│  "Ensure all rivalry games are on weekends on ESPN"         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: Template Classification (Vector Search)           │
│  • Generate embedding with text-embedding-3-small            │
│  • Cosine similarity search in Supabase pgvector             │
│  • Returns: Template ID + Confidence Score                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: Parameter Extraction (LLM)                         │
│  • GPT-4o-mini with JSON mode                                │
│  • Extract: min, max, teams, rounds, networks, venues        │
│  • Handle negations: "don't" → max=0                         │
│  • Returns: Structured parameters                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: Feasibility Warning (Rule-based)                   │
│  • Validate parameter constraints                            │
│  • Check logical consistency                                 │
│  • Generate warnings and suggestions                         │
│  • Returns: Feasibility score + feedback                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Structured Output                         │
│  Template 1: Game Scheduling (94% confidence)               │
│  Constraint: "Ensure that at least 1 and at most 999..."    │
│  Feasibility: ✓ Feasible (87% confidence)                   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **Database**: Supabase (PostgreSQL + pgvector)
- **AI/ML**: OpenAI (text-embedding-3-small + GPT-4o-mini)
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui (Radix UI primitives)
- **Deployment**: Vercel

## 📋 Constraint Templates

### Template 1: Game Scheduling
Ensures specific games are scheduled in certain rounds, venues, and networks.

**Example**: "Ensure all rivalry games are scheduled on weekends and broadcast on ESPN"

### Template 2: Time Slot Constraints
Limits games in specific time slots for networks.

**Example**: "Limit ESPN to maximum 2 games in primetime slots"

### Template 3: Team-specific Constraints
Applies schedule pattern constraints to specific teams.

**Example**: "Ensure Lakers have at least 2 rest days between back-to-back games"

## 🛠️ Installation

### Prerequisites

- Node.js 18+ or 20+
- npm or yarn
- Supabase account
- OpenAI API key

### Quick Start

```bash
# Clone the repository
git clone https://github.com/mkommar/sports-scheduling-constraint-parser.git
cd sports-scheduling-constraint-parser

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your credentials

# Run database migrations in Supabase
# (See DEPLOYMENT.md for detailed instructions)

# Seed the database
npm run dev  # Start dev server
curl -X POST http://localhost:3000/api/seed

# Open the app
# Visit http://localhost:3000
```

## 📝 Environment Variables

Create `.env.local` in the project root:

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key
```

## 🎨 Features

### Core Functionality
- ✅ Natural language query parsing
- ✅ Vector similarity search with pgvector
- ✅ LLM-powered parameter extraction
- ✅ Rule-based feasibility checking
- ✅ Real-time confidence scores
- ✅ Structured constraint generation

### UI/UX
- ✅ Modern, responsive design
- ✅ shadcn/ui components
- ✅ Loading states and error handling
- ✅ Expandable parameter views
- ✅ Detailed explanations
- ✅ Example query suggestions

### Developer Experience
- ✅ TypeScript strict mode
- ✅ Type-safe API routes
- ✅ Modular architecture
- ✅ Comprehensive documentation
- ✅ Easy deployment to Vercel

## 📦 Project Structure

```
sports-scheduling-constraint-parser/
├── app/
│   ├── api/
│   │   ├── parse/route.ts         # Main parsing endpoint
│   │   └── seed/route.ts          # Database seeding endpoint
│   ├── globals.css                # Global styles
│   ├── layout.tsx                 # Root layout
│   └── page.tsx                   # Home page
├── components/
│   ├── ui/                        # shadcn/ui components
│   │   ├── accordion.tsx
│   │   ├── avatar.tsx
│   │   ├── badge.tsx
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── input.tsx
│   ├── navbar.tsx                 # Navigation component
│   ├── search-input.tsx           # Search input component
│   └── search-result.tsx          # Result display component
├── lib/
│   ├── feasibility.ts             # Stage 3: Feasibility checking
│   ├── openai.ts                  # OpenAI integration
│   ├── supabase.ts                # Supabase client
│   ├── templates.ts               # Constraint templates
│   └── utils.ts                   # Utility functions
├── scripts/
│   └── seed-database.ts           # Database seeding script
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql # Database schema
├── .env.local.example             # Environment variables template
├── DEPLOYMENT.md                  # Deployment guide
├── README.md                      # This file
├── next.config.js                 # Next.js configuration
├── package.json                   # Dependencies
├── tailwind.config.ts             # Tailwind configuration
├── tsconfig.json                  # TypeScript configuration
└── vercel.json                    # Vercel configuration
```

## 🔌 API Endpoints

### POST `/api/parse`

Parse a natural language query into a structured constraint.

**Request**:
```json
{
  "query": "Ensure all rivalry games are scheduled on weekends and broadcast on ESPN"
}
```

**Response**:
```json
{
  "templateId": 1,
  "templateName": "Game Scheduling",
  "confidence": 0.94,
  "constraintSentence": "Ensure that at least 1 and at most 999 games from rivalry_games are scheduled across weekend_rounds and played in any venue from all_venues and assigned to ESPN.",
  "parameters": {
    "min": 1,
    "max": 999,
    "teams": "rivalry_games",
    "rounds": "weekend_rounds",
    "networks": "ESPN",
    "venues": "all_venues"
  },
  "feasibility": {
    "feasible": true,
    "confidence": 0.87,
    "warnings": [],
    "suggestions": ["This constraint appears feasible and well-formed"]
  },
  "matchReason": "Semantic similarity: 94%"
}
```

### POST `/api/seed`

Seed the database with example queries and embeddings.

**Response**:
```json
{
  "success": true,
  "message": "Seeded 15 example queries",
  "count": 15
}
```

## 🚢 Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive deployment instructions.

### Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/sports-scheduling-constraint-parser)

1. Click the button above
2. Add environment variables
3. Deploy!

Don't forget to:
1. Set up Supabase and run migrations
2. Seed the database: `curl -X POST https://your-app.vercel.app/api/seed`

## 🧪 Testing

### Manual Testing

Login with the demo Vercel URL:
URL: https://sports-scheduling-constraint-parser-dun.vercel.app/
Username: mahesh.kommareddi+vendor@gmail.com
Password: r'24L.Ug6tsvQ?z

Try these example queries:

1. **Game Scheduling**:
   - "Ensure all rivalry games are scheduled on weekends and broadcast on ESPN"
   - "Schedule division games on FOX during weekend rounds"
   - "Don't schedule rivalry games on weekdays"

2. **Time Slot Constraints**:
   - "Limit ESPN to maximum 2 games in primetime slots"
   - "Ensure FOX broadcasts at least 1 game during afternoon slots"
   - "No more than 2 concurrent games on NBC during primetime"

3. **Team-specific Constraints**:
   - "Ensure Lakers have at least 2 rest days between back-to-back games"
   - "Limit Warriors to maximum 3 consecutive home games"
   - "Don't schedule Knicks for more than 2 consecutive away games"

## 🎯 ML Engineering Highlights

### Why This Architecture?

1. **Vector Search for Template Classification**
   - Fast, scalable matching using pgvector
   - No need to retrain models for new examples
   - Easily extensible with more templates

2. **LLM for Parameter Extraction**
   - Handles natural language variations
   - JSON mode ensures structured output
   - Low latency with GPT-4o-mini

3. **Rule-based Feasibility (MVP)**
   - Immediate feedback without ML training
   - Transparent, explainable logic
   - Foundation for future XGBoost enhancement

### Future Enhancements

- [ ] XGBoost model for advanced feasibility prediction
- [ ] Fine-tuned model for parameter extraction
- [ ] Multi-modal support (upload schedule documents)
- [ ] Constraint conflict detection
- [ ] Historical query analytics
- [ ] A/B testing framework

## 🔒 Security

- ✅ Environment variables for sensitive keys
- ✅ Server-side API key usage only
- ✅ Supabase Row Level Security (RLS)
- ✅ TypeScript for type safety
- ✅ Input validation and sanitization

## 📊 Performance

- **Embedding generation**: ~200ms
- **Vector search**: ~50ms
- **LLM parameter extraction**: ~500-800ms
- **Total pipeline**: ~800-1200ms
- **Cold start**: ~2-3s (Vercel serverless)

## 💰 Cost Analysis

For 10,000 queries/month:
- OpenAI API: ~$10
- Supabase: Free tier (or $25/mo for Pro)
- Vercel: Free tier
- **Total: $10-35/month**

## 🤝 Contributing

This is a challenge project, but suggestions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details

## 👤 Author

Built for the Fastbreak.ai ML Engineer role challenge

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/) - React framework
- [Supabase](https://supabase.com/) - Backend platform
- [OpenAI](https://openai.com/) - AI models
- [shadcn/ui](https://ui.shadcn.com/) - Component library
- [Vercel](https://vercel.com/) - Deployment platform

---

**⚡ Built with production ML engineering best practices**

For questions or feedback, please open an issue or reach out!
