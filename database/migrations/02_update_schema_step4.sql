-- Step 8: Verify data migration
SELECT COUNT(*) as user_count FROM users;
SELECT COUNT(*) as user_credits_count FROM user_credits;
SELECT COUNT(*) as stats_count FROM user_stats;
SELECT COUNT(*) as transactions_count FROM transactions;
SELECT COUNT(*) as credit_history_count FROM credit_history;

-- If counts match and data is verified, run these commands:
-- DROP TABLE IF EXISTS credit_history;
-- DROP TABLE IF EXISTS user_credits;
