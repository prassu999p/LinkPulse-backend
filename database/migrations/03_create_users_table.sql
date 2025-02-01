-- First, check if users table exists and drop it if it does (since it's empty/incorrect)
DROP TABLE IF EXISTS users;

-- Create the users table with all required columns
CREATE TABLE users (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id),
    email TEXT NOT NULL UNIQUE,
    credits INTEGER NOT NULL DEFAULT 50,
    full_name TEXT,
    company TEXT,
    job_title TEXT,
    linkedin_profile TEXT,
    preferred_tone TEXT,
    notification_preferences JSONB DEFAULT '{"email_notifications": true, "credit_alerts": true}',
    total_posts_generated INTEGER DEFAULT 0,
    total_credits_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_credits ON users(credits);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view their own profile"
    ON users FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile"
    ON users FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Service role can manage all users"
    ON users FOR ALL
    USING (auth.role() = 'service_role');

-- Create updated_at trigger
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Migrate data from user_credits to users
INSERT INTO users (
    user_id,
    email,
    credits,
    full_name,
    company,
    job_title,
    linkedin_profile,
    preferred_tone,
    notification_preferences,
    total_posts_generated,
    total_credits_used,
    created_at,
    updated_at
)
SELECT 
    uc.user_id,
    au.email,
    uc.credits,
    uc.full_name,
    uc.company,
    uc.job_title,
    uc.linkedin_profile,
    uc.preferred_tone,
    uc.notification_preferences,
    uc.total_posts_generated,
    uc.total_credits_used,
    uc.created_at,
    uc.updated_at
FROM user_credits uc
JOIN auth.users au ON au.id = uc.user_id
ON CONFLICT (user_id) DO UPDATE SET
    credits = EXCLUDED.credits,
    full_name = EXCLUDED.full_name,
    company = EXCLUDED.company,
    job_title = EXCLUDED.job_title,
    linkedin_profile = EXCLUDED.linkedin_profile,
    preferred_tone = EXCLUDED.preferred_tone,
    notification_preferences = EXCLUDED.notification_preferences,
    total_posts_generated = EXCLUDED.total_posts_generated,
    total_credits_used = EXCLUDED.total_credits_used,
    updated_at = NOW();
