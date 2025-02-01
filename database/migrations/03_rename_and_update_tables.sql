-- Step 1: Rename user_credits to user_profiles
ALTER TABLE IF EXISTS user_credits 
    RENAME TO user_profiles;

-- Step 2: Create user_stats table
CREATE TABLE IF NOT EXISTS user_stats (
    user_id UUID PRIMARY KEY,
    total_posts_generated INTEGER DEFAULT 0,
    total_credits_used INTEGER DEFAULT 0,
    remaining_credits INTEGER DEFAULT 50,
    last_login TIMESTAMPTZ DEFAULT NOW(),
    account_created TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Step 3: Create transactions table
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
CREATE INDEX IF NOT EXISTS idx_user_profiles_credits ON user_profiles(credits);
CREATE INDEX IF NOT EXISTS idx_user_stats_user_id ON user_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);

-- Step 5: Set up RLS policies
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Policies for user_profiles
CREATE POLICY "Users can view their own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Service role can manage all profiles"
    ON user_profiles FOR ALL
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
