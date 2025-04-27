-- Seed projects
INSERT INTO projects (id, name, api_key) VALUES
  ('proj_123', 'Test Project', 'test_api_key_123'),
  ('proj_456', 'Demo Project', 'demo_api_key_456');

-- Seed devices
INSERT INTO devices (project_id, user_id, device_id, platform, token) VALUES
  ('proj_123', 'user_1', 'device_1', 'ios', 'ios_push_token_1'),
  ('proj_123', 'user_1', 'device_2', 'android', 'android_push_token_1'),
  ('proj_123', 'user_2', 'device_3', 'ios', 'ios_push_token_2'),
  ('proj_456', 'user_3', 'device_4', 'android', 'android_push_token_2');

-- Seed messages
INSERT INTO messages (project_id, user_id, title, body, category) VALUES
  ('proj_123', 'user_1', 'Welcome!', 'Welcome to our app!', 'news'),
  ('proj_123', 'user_2', 'New Feature', 'Check out our latest feature!', 'updates'),
  ('proj_456', 'user_3', 'Important Update', 'Please update your app.', 'news'); 