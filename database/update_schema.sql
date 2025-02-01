-- Create user_credits table (instead of renaming users)
CREATE TABLE IF NOT EXISTS user_credits (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id),
    credits INTEGER NOT NULL DEFAULT 50,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create credit_history table (instead of renaming transactions)
CREATE TABLE IF NOT EXISTS credit_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    amount INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_credits_credits ON user_credits(credits);
CREATE INDEX IF NOT EXISTS idx_credit_history_created_at ON credit_history(created_at);
CREATE INDEX IF NOT EXISTS idx_credit_history_user_id ON credit_history(user_id);

-- Create updated_at trigger for user_credits
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

-- Enable RLS
ALTER TABLE user_credits ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_history ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own credits" ON user_credits;
DROP POLICY IF EXISTS "Service role can manage all credits" ON user_credits;
DROP POLICY IF EXISTS "Users can view their own credit history" ON credit_history;
DROP POLICY IF EXISTS "Service role can manage all credit history" ON credit_history;

-- Create new policies
CREATE POLICY "Users can view their own credits"
    ON user_credits FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage all credits"
    ON user_credits FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Users can view their own credit history"
    ON credit_history FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage all credit history"
    ON credit_history FOR ALL
    USING (auth.role() = 'service_role'); 