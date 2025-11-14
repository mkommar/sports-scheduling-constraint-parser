-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create constraint_examples table
CREATE TABLE IF NOT EXISTS constraint_examples (
  id BIGSERIAL PRIMARY KEY,
  template_id INTEGER NOT NULL,
  content TEXT NOT NULL UNIQUE,
  embedding vector(1536),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS constraint_examples_embedding_idx 
  ON constraint_examples 
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Create function for matching templates based on similarity
CREATE OR REPLACE FUNCTION match_templates (
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 3
)
RETURNS TABLE (
  id bigint,
  template_id integer,
  content text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    constraint_examples.id,
    constraint_examples.template_id,
    constraint_examples.content,
    1 - (constraint_examples.embedding <=> query_embedding) as similarity
  FROM constraint_examples
  WHERE 1 - (constraint_examples.embedding <=> query_embedding) > match_threshold
  ORDER BY constraint_examples.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Create RLS policies (optional, for production use with auth)
ALTER TABLE constraint_examples ENABLE ROW LEVEL SECURITY;

-- Allow public read access (modify as needed for your use case)
CREATE POLICY "Allow public read access" 
  ON constraint_examples 
  FOR SELECT 
  TO public 
  USING (true);

-- Allow service role full access
CREATE POLICY "Allow service role full access" 
  ON constraint_examples 
  FOR ALL 
  TO service_role 
  USING (true);

