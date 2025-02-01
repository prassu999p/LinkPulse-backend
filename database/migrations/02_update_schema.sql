-- Step 1: Create new users table with the same structure as user_credits
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
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

-- Step 2: Create user_stats table
CREATE TABLE IF NOT EXISTS user_stats (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    total_posts_generated INTEGER DEFAULT 0,
    total_credits_used INTEGER DEFAULT 0,
    remaining_credits INTEGER DEFAULT 50,
    last_login TIMESTAMPTZ DEFAULT NOW(),
    account_created TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Step 3: Create transactions table for credit history
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    amount INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Step 4: Migrate data from user_credits to users
INSERT INTO users (
    id,
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
ON CONFLICT (id) DO NOTHING;

-- Step 5: Migrate data to user_stats
INSERT INTO user_stats (
    user_id,
    total_posts_generated,
    total_credits_used,
    remaining_credits,
    account_created
)
SELECT 
    id,
    total_posts_generated,
    total_credits_used,
    credits,
    created_at
FROM users
ON CONFLICT (user_id) DO NOTHING;

-- Step 6: Migrate credit history
INSERT INTO transactions (
    user_id,
    amount,
    action_type,
    description,
    created_at
)
SELECT 
    user_id,
    amount,
    action_type,
    description,
    created_at
FROM credit_history
ON CONFLICT (id) DO NOTHING;

-- Step 7: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_credits ON users(credits);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_stats_user_id ON user_stats(user_id);

-- Step 8: Create updated_at trigger for users table
CREATE OR REPLACE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Step 9: Set up RLS policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Policies for users table
CREATE POLICY "Users can view their own profile"
    ON users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON users FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Service role can manage all users"
    ON users FOR ALL
    USING (auth.role() = 'service_role');

-- Policies for user_stats
CREATE POLICY "Users can view their own stats"
    ON user_stats FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage all stats"
    ON user_stats FOR ALL
    USING (auth.role() = 'service_role');

-- Policies for transactions
CREATE POLICY "Users can view their own transactions"
    ON transactions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage all transactions"
    ON transactions FOR ALL
    USING (auth.role() = 'service_role');

-- Step 10: Drop old tables (ONLY AFTER VERIFYING DATA MIGRATION)
-- NOTE: Comment these out first, verify the migration, then run them separately
-- DROP TABLE IF EXISTS credit_history;
-- DROP TABLE IF EXISTS user_credits;
