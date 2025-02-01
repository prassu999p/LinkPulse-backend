-- Step 4: Migrate data
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

-- Step 5: Migrate stats
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
