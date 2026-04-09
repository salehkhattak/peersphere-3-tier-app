-- PeerSphere Stored Procedures

-- Procedure: Find users with similar skills
CREATE OR REPLACE FUNCTION find_similar_users(p_skill_id INTEGER, p_user_id INTEGER DEFAULT NULL)
RETURNS TABLE (
    user_id INTEGER,
    user_name VARCHAR,
    email VARCHAR,
    university VARCHAR,
    department VARCHAR,
    shared_skills BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.id AS user_id,
        u.name AS user_name,
        u.email,
        u.university,
        u.department,
        COUNT(us.skill_id) AS shared_skills
    FROM users u
    JOIN user_skills us ON u.id = us.user_id
    WHERE us.skill_id = p_skill_id
    AND (p_user_id IS NULL OR u.id != p_user_id)
    GROUP BY u.id, u.name, u.email, u.university, u.department
    ORDER BY shared_skills DESC;
END;
$$ LANGUAGE plpgsql;
