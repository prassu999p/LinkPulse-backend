-- Step 1: Create new tables
CREATE TABLE IF NOT EXISTS user_credits (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id),
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

CREATE TABLE IF NOT EXISTS credit_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    amount INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Step 2: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_credits_credits ON user_credits(credits);
CREATE INDEX IF NOT EXISTS idx_credit_history_created_at ON credit_history(created_at);
CREATE INDEX IF NOT EXISTS idx_credit_history_user_id ON credit_history(user_id);

-- Step 3: Migrate data from old transactions table to credit_history
INSERT INTO credit_history (user_id, amount, action_type, created_at)
SELECT user_id, credit_change, action_type, created_at
FROM transactions;

-- Step 4: Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_credits_updated_at
    BEFORE UPDATE ON user_credits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Step 5: Create post generation stats trigger
CREATE OR REPLACE FUNCTION update_post_generation_stats()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE user_credits
  SET 
    total_posts_generated = total_posts_generated + 1,
    total_credits_used = total_credits_used + NEW.amount
  WHERE user_id = NEW.user_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_post_generated
  AFTER INSERT ON credit_history
  FOR EACH ROW
  WHEN (NEW.action_type = 'post_generation')
  EXECUTE FUNCTION update_post_generation_stats();

-- Step 6: Set up RLS policies
ALTER TABLE user_credits ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_history ENABLE ROW LEVEL SECURITY;

-- Policies for user_credits
CREATE POLICY "Users can view their own credits"
    ON user_credits FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile"
    ON user_credits FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Service role can manage all credits"
    ON user_credits FOR ALL
    USING (auth.role() = 'service_role');

-- Policies for credit_history
CREATE POLICY "Users can view their own credit history"
    ON credit_history FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage all credit history"
    ON credit_history FOR ALL
    USING (auth.role() = 'service_role');

-- Step 7: Drop old transactions table (ONLY AFTER VERIFYING DATA MIGRATION)
-- NOTE: Comment this out first, verify the migration, then run it separately
-- DROP TABLE IF EXISTS transactions; 