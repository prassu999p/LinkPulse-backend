-- Step 5: Migrate stats
INSERT INTO user_stats (
    user_id,
    total_posts_generated,
    total_credits_used,
    remaining_credits,
    account_created
)
SELECT 
    user_id,
    total_posts_generated,
    total_credits_used,
    credits,
    created_at
FROM user_credits
ON CONFLICT (user_id) DO NOTHING;

-- Step 6: Migrate transactions
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
