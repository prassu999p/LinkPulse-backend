-- Step 1: Create backup tables
CREATE TABLE IF NOT EXISTS user_credits_backup AS 
SELECT * FROM user_credits;

CREATE TABLE IF NOT EXISTS credit_history_backup AS 
SELECT * FROM credit_history;

-- Step 2: Create new tables
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

CREATE TABLE IF NOT EXISTS user_stats (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    total_posts_generated INTEGER DEFAULT 0,
    total_credits_used INTEGER DEFAULT 0,
    remaining_credits INTEGER DEFAULT 50,
    last_login TIMESTAMPTZ DEFAULT NOW(),
    account_created TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    amount INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Step 3: Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_credits ON users(credits);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_stats_user_id ON user_stats(user_id);
