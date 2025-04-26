# Push API Setup Guide

## Project Structure
```
push-api/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── devices.py
│   │   ├── messages.py
│   │   └── preferences.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── device.py
│   │   ├── message.py
│   │   └── preference.py
│   └── services/
│       ├── __init__.py
│       ├── push.py
│       └── supabase.py
├── supabase/
│   ├── migrations/
│   │   ├── 20240101000000_initial_schema.sql
│   │   └── 20240101000001_add_indexes.sql
│   └── seed.sql
├── functions/
│   └── push-api/
│       ├── index.ts
│       └── package.json
├── config.py
├── requirements.txt
└── run.py
```

## Local Development Setup

### 1. Supabase Setup

#### Install Supabase CLI
```bash
# macOS
brew install supabase/tap/supabase

# Windows
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase
```

#### Initialize Supabase
```bash
# Create new project
supabase init

# Start local Supabase
supabase start
```

#### Link to Remote Project
```bash
# Get project reference from Supabase dashboard
supabase link --project-ref your-project-ref

# Pull remote database schema
supabase db pull
```

### 2. Database Migrations

Migrations are stored in `supabase/migrations/` and follow the naming convention:
```
YYYYMMDDHHMMSS_description.sql
```

Example migration:
```sql
-- supabase/migrations/20240101000000_initial_schema.sql
create table devices (
  id text primary key,
  user_id text not null,
  platform text not null,
  token text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);

create table preferences (
  user_id text primary key,
  enabled boolean default true,
  categories jsonb default '{}'::jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);

create table messages (
  id text primary key,
  user_id text not null,
  title text not null,
  body text not null,
  platform text,
  device_id text,
  category text,
  status text default 'sent',
  created_at timestamp with time zone default timezone('utc'::text, now())
);
```

Apply migrations:
```bash
# Apply all migrations
supabase db reset

# Apply specific migration
supabase db reset --db-only
```

### 3. Local API Development

#### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
```

#### Environment Variables
```bash
# .env
SUPABASE_URL=http://localhost:54321
SUPABASE_KEY=your-local-anon-key
SUPABASE_SERVICE_KEY=your-local-service-key
API_KEY=your-api-key
```

#### Run Local API
```bash
# Run Flask development server
flask run
```

## Supabase Edge Functions

The API can be deployed as a Supabase Edge Function. Here's how to structure it:

### 1. Function Setup
```bash
# Create new function
supabase functions new push-api
```

### 2. Function Structure
```typescript
// functions/push-api/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Create Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? ''
    )

    // Handle API routes
    const url = new URL(req.url)
    const path = url.pathname

    if (path.startsWith('/v1/devices')) {
      // Handle device registration
    } else if (path.startsWith('/v1/messages')) {
      // Handle message sending
    } else if (path.startsWith('/v1/preferences')) {
      // Handle preferences
    }

    return new Response(
      JSON.stringify({ error: 'Not found' }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 404 
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400 
      }
    )
  }
})
```

### 3. Deploy Function
```bash
# Deploy to Supabase
supabase functions deploy push-api
```

## Testing

### Local Testing
```bash
# Start local Supabase
supabase start

# Run tests
pytest

# Test API endpoints
curl -X POST http://localhost:5000/v1/devices/user123/device123 \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"platform": "ios", "deviceToken": "token123"}'
```

### Production Testing
```bash
# Test deployed function
curl -X POST https://your-project.supabase.co/functions/v1/push-api/v1/devices/user123/device123 \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"platform": "ios", "deviceToken": "token123"}'
```

## Best Practices

1. **Database Migrations**
   - Always create migrations for schema changes
   - Test migrations locally before deploying
   - Use meaningful migration names

2. **Local Development**
   - Use Supabase CLI for local development
   - Keep local and production schemas in sync
   - Use environment variables for configuration

3. **Edge Functions**
   - Keep functions small and focused
   - Handle CORS properly
   - Implement proper error handling
   - Use TypeScript for better type safety

## Next Steps

1. Set up CI/CD pipeline
2. Add monitoring and logging
3. Implement rate limiting
4. Add comprehensive testing
5. Set up staging environment 