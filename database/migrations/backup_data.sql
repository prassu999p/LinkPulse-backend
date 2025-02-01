-- Backup user_credits data
CREATE TABLE IF NOT EXISTS user_credits_backup AS 
SELECT * FROM user_credits;

-- Backup credit_history data
CREATE TABLE IF NOT EXISTS credit_history_backup AS 
SELECT * FROM credit_history;
