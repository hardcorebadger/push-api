-- Insert test project
INSERT INTO projects (id, name, api_key) 
VALUES 
  ('test-project-1', 'Test Project 1', 'test-api-key-1'),
  ('test-project-2', 'Test Project 2', 'test-api-key-2');

-- Insert sample devices for test-project-1
INSERT INTO devices (device_id, user_id, platform, token, project_id)
VALUES 
  ('ios-device-1', 'user-1', 'ios', 'ios-token-1', 'test-project-1'),
  ('android-device-1', 'user-1', 'android', 'android-token-1', 'test-project-1'),
  ('web-device-1', 'user-2', 'web', 'web-token-1', 'test-project-1');

-- Insert sample devices for test-project-2
INSERT INTO devices (device_id, user_id, platform, token, project_id)
VALUES 
  ('ios-device-2', 'user-3', 'ios', 'ios-token-2', 'test-project-2'),
  ('android-device-2', 'user-3', 'android', 'android-token-2', 'test-project-2');

-- Insert sample user preferences for test-project-1
INSERT INTO preferences (user_id, enabled, categories, project_id)
VALUES 
  ('user-1', true, array['marketing', 'security'], 'test-project-1'),
  ('user-2', true, array['security'], 'test-project-1');

-- Insert sample user preferences for test-project-2
INSERT INTO preferences (user_id, enabled, categories, project_id)
VALUES 
  ('user-3', true, array['marketing', 'security'], 'test-project-2');

-- Insert sample device preferences for test-project-1
INSERT INTO device_preferences (device_id, enabled, categories)
VALUES 
  (1, true, array['marketing', 'security']),  -- user-1's iOS device, accepts all
  (2, true, array['security']),               -- user-1's Android device, security only
  (3, true, array['security']);               -- user-2's web device, security only

-- Insert sample device preferences for test-project-2
INSERT INTO device_preferences (device_id, enabled, categories)
VALUES 
  (4, true, array['marketing', 'security']),  -- user-3's iOS device, accepts all
  (5, false, array[]::text[]);                -- user-3's Android device, disabled

-- Insert sample messages for test-project-1
INSERT INTO messages (user_id, title, body, category, project_id)
VALUES 
  ('user-1', 'Welcome', 'Welcome to our app!', 'marketing', 'test-project-1'),
  ('user-2', 'Security Alert', 'New login detected', 'security', 'test-project-1'),
  ('user-1', 'System Update', 'Your app has been updated', null, 'test-project-1');

-- Insert sample messages for test-project-2
INSERT INTO messages (user_id, title, body, category, project_id)
VALUES 
  ('user-3', 'Welcome', 'Welcome to our app!', 'marketing', 'test-project-2');

-- Insert sample sends for test-project-1 messages
INSERT INTO sends (message_id, device_id, platform, status, delivered_at)
VALUES 
  -- Marketing message (id: 1) - should only go to user-1's iOS device
  (1, 1, 'ios', 'delivered', now()),
  -- Security message (id: 2) - should go to all devices
  (2, 1, 'ios', 'delivered', now()),
  (2, 2, 'android', 'delivered', now()),
  (2, 3, 'web', 'failed', null),
  -- System message (id: 3) - should go to all devices (no category)
  (3, 1, 'ios', 'delivered', now()),
  (3, 2, 'android', 'delivered', now()),
  (3, 3, 'web', 'pending', null);

-- Insert sample sends for test-project-2 messages
INSERT INTO sends (message_id, device_id, platform, status, delivered_at)
VALUES 
  -- Marketing message (id: 4) - should only go to user-3's iOS device (Android disabled)
  (4, 4, 'ios', 'delivered', now()); 