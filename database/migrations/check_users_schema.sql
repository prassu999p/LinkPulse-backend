-- Check current schema
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- Create an alter table statement to add any missing columns we need
DO $$ 
BEGIN 
    -- Add email if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'email') THEN
        ALTER TABLE users ADD COLUMN email TEXT NOT NULL UNIQUE;
    END IF;

    -- Add credits if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'credits') THEN
        ALTER TABLE users ADD COLUMN credits INTEGER NOT NULL DEFAULT 50;
    END IF;

    -- Add full_name if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'full_name') THEN
        ALTER TABLE users ADD COLUMN full_name TEXT;
    END IF;

    -- Add company if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'company') THEN
        ALTER TABLE users ADD COLUMN company TEXT;
    END IF;

    -- Add job_title if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'job_title') THEN
        ALTER TABLE users ADD COLUMN job_title TEXT;
    END IF;

    -- Add linkedin_profile if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'linkedin_profile') THEN
        ALTER TABLE users ADD COLUMN linkedin_profile TEXT;
    END IF;

    -- Add preferred_tone if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'preferred_tone') THEN
        ALTER TABLE users ADD COLUMN preferred_tone TEXT;
    END IF;

    -- Add notification_preferences if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'notification_preferences') THEN
        ALTER TABLE users ADD COLUMN notification_preferences JSONB DEFAULT '{"email_notifications": true, "credit_alerts": true}';
    END IF;

    -- Add total_posts_generated if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'total_posts_generated') THEN
        ALTER TABLE users ADD COLUMN total_posts_generated INTEGER DEFAULT 0;
    END IF;

    -- Add total_credits_used if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'total_credits_used') THEN
        ALTER TABLE users ADD COLUMN total_credits_used INTEGER DEFAULT 0;
    END IF;

    -- Add created_at if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'created_at') THEN
        ALTER TABLE users ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
    END IF;

    -- Add updated_at if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'updated_at') THEN
        ALTER TABLE users ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
    END IF;

END $$;

-- Check schema again after potential modifications
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- Check if we have the necessary indexes
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'users';

-- Create any missing indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_credits ON users(credits);
