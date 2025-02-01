-- Step 7: Set up RLS policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Policies for users table
CREATE POLICY "Users can view their own profile"
    ON users FOR SELECT
    USING (auth.uid() = user_id);  -- Changed from 'id' to 'user_id'

CREATE POLICY "Users can update their own profile"
    ON users FOR UPDATE
    USING (auth.uid() = user_id)  -- Changed from 'id' to 'user_id'
    WITH CHECK (auth.uid() = user_id);  -- Changed from 'id' to 'user_id'

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
