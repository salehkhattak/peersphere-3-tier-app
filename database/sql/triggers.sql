-- PeerSphere SQL Triggers
-- These are for PostgreSQL. For SQLite, triggers are handled at the application layer.

-- Trigger: Log when a user joins a community
CREATE OR REPLACE FUNCTION log_community_join()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO activity_log (user_id, action, target_type, target_id, timestamp)
    VALUES (NEW.user_id, 'Joined community', 'community', NEW.community_id, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_community_join
AFTER INSERT ON community_members
FOR EACH ROW
EXECUTE FUNCTION log_community_join();


-- Trigger: Log when a user joins an event
CREATE OR REPLACE FUNCTION log_event_join()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO activity_log (user_id, action, target_type, target_id, timestamp)
    VALUES (NEW.user_id, 'Joined event', 'event', NEW.event_id, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_event_join
AFTER INSERT ON event_attendees
FOR EACH ROW
EXECUTE FUNCTION log_event_join();
