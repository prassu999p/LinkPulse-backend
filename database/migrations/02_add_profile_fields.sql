-- Add profile fields to user_credits table
ALTER TABLE user_credits
ADD COLUMN IF NOT EXISTS full_name TEXT,
ADD COLUMN IF NOT EXISTS company TEXT,
ADD COLUMN IF NOT EXISTS job_title TEXT,
ADD COLUMN IF NOT EXISTS linkedin_profile TEXT,
ADD COLUMN IF NOT EXISTS preferred_tone TEXT,
ADD COLUMN IF NOT EXISTS notification_preferences JSONB DEFAULT '{"email_notifications": true, "credit_alerts": true}',
ADD COLUMN IF NOT EXISTS total_posts_generated INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_credits_used INTEGER DEFAULT 0;

-- Create function to update post generation stats
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

-- Create trigger for post generation stats
DROP TRIGGER IF EXISTS on_post_generated ON credit_history;
CREATE TRIGGER on_post_generated
  AFTER INSERT ON credit_history
  FOR EACH ROW
  WHEN (NEW.action_type = 'post_generation')
  EXECUTE FUNCTION update_post_generation_stats(); 