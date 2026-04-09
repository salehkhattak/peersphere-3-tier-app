-- PeerSphere SQL Views

-- View: Popular Communities (ranked by member count)
CREATE OR REPLACE VIEW popular_communities_view AS
SELECT
    c.id,
    c.name,
    c.description,
    c.created_at,
    COUNT(cm.id) AS member_count
FROM communities c
LEFT JOIN community_members cm ON c.id = cm.community_id
GROUP BY c.id, c.name, c.description, c.created_at
ORDER BY member_count DESC;


-- View: Active Users (ranked by activity: posts + comments + likes)
CREATE OR REPLACE VIEW active_users_view AS
SELECT
    u.id,
    u.name,
    u.email,
    u.university,
    u.department,
    COALESCE(p.post_count, 0) AS post_count,
    COALESCE(c.comment_count, 0) AS comment_count,
    COALESCE(l.like_count, 0) AS like_count,
    (COALESCE(p.post_count, 0) + COALESCE(c.comment_count, 0) + COALESCE(l.like_count, 0)) AS total_activity
FROM users u
LEFT JOIN (SELECT user_id, COUNT(*) AS post_count FROM posts GROUP BY user_id) p ON u.id = p.user_id
LEFT JOIN (SELECT user_id, COUNT(*) AS comment_count FROM comments GROUP BY user_id) c ON u.id = c.user_id
LEFT JOIN (SELECT user_id, COUNT(*) AS like_count FROM likes GROUP BY user_id) l ON u.id = l.user_id
ORDER BY total_activity DESC;
