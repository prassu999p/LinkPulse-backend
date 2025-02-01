-- Drop existing policies
DROP POLICY IF EXISTS "Users can view their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Service role can manage all profiles" ON user_profiles;

-- Create new policies
CREATE POLICY "Enable read for users based on user_id" ON user_profiles
    FOR SELECT USING (
        auth.uid() = user_id
        OR auth.role() = 'service_role'
        OR auth.role() = 'authenticated'
    );

CREATE POLICY "Enable insert for service role" ON user_profiles
    FOR INSERT WITH CHECK (
        auth.role() = 'service_role'
        OR auth.role() = 'authenticated'
    );

CREATE POLICY "Enable update for users based on user_id" ON user_profiles
    FOR UPDATE USING (
        auth.uid() = user_id
        OR auth.role() = 'service_role'
        OR auth.role() = 'authenticated'
    )
    WITH CHECK (
        auth.uid() = user_id
        OR auth.role() = 'service_role'
        OR auth.role() = 'authenticated'
    );

CREATE POLICY "Enable delete for service role" ON user_profiles
    FOR DELETE USING (
        auth.role() = 'service_role'
    );
