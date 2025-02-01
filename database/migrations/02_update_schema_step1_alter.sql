-- Step 1: Create backup tables
CREATE TABLE IF NOT EXISTS user_credits_backup AS 
SELECT * FROM user_credits;

CREATE TABLE IF NOT EXISTS credit_history_backup AS 
SELECT * FROM credit_history;

-- Step 2: Create user_stats table if it doesn't exist
CREATE TABLE IF NOT EXISTS user_stats (
    user_id UUID PRIMARY KEY,
    total_posts_generated INTEGER DEFAULT 0,
    total_credits_used INTEGER DEFAULT 0,
    remaining_credits INTEGER DEFAULT 50,
    last_login TIMESTAMPTZ DEFAULT NOW(),
    account_created TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Step 3: Create transactions table for credit history
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    amount INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Step 4: Create indexes
CREATE INDEX IF NOT EXISTS idx_user_stats_user_id ON user_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
