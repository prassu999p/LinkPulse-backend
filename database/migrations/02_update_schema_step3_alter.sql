-- Step 7: Set up RLS policies
ALTER TABLE user_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

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
