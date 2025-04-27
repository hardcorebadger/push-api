-- Seed projects
INSERT INTO projects (id, name, api_key, vapid_public_key, vapid_private_key, vapid_subject) VALUES
  ('proj_123', 'Test Project', 'test_api_key_123',
  'BL1UTG9y___ns5iHj5yI-LnDUmm4Ys5yD18H3yUVRKDKiBXaF_fvU-UpH0jpfv2Mnl4VgP-H0Op5pLTkZvwO6_M',
  'QrHprlTqnTwmnAIc5GNXsGpAWWFiwJyFoOIX5Gs-9Kw',
  'mailto:admin@mail.com'),

  ('proj_456', 'Demo Project', 'demo_api_key_456',
  'BL1UTG9y___ns5iHj5yI-LnDUmm4Ys5yD18H3yUVRKDKiBXaF_fvU-UpH0jpfv2Mnl4VgP-H0Op5pLTkZvwO6_M',
  'QrHprlTqnTwmnAIc5GNXsGpAWWFiwJyFoOIX5Gs-9Kw',
  'mailto:admin@mail.com');

-- Seed devices
INSERT INTO devices (project_id, user_id, device_id, platform, token) VALUES
  ('proj_123', 'user_1', 'device_1', 'ios', 'ios_push_token_1'),
  ('proj_123', 'user_1', 'device_2', 'android', 'android_push_token_1'),
  ('proj_123', 'user_2', 'device_3', 'ios', 'ios_push_token_2'),
  ('proj_456', 'user_3', 'device_4', 'android', 'android_push_token_2');

-- Seed messages
INSERT INTO messages (project_id, user_id, title, body, category, icon, action_url) VALUES
  ('proj_123', 'user_1', 'Welcome!', 'Welcome to our app!', 'news', 'https://example.com/icon1.png', 'https://example.com/welcome'),
  ('proj_123', 'user_2', 'New Feature', 'Check out our latest feature!', 'updates', NULL, NULL),
  ('proj_456', 'user_3', 'Important Update', 'Please update your app.', 'news', NULL, 'https://example.com/update'); 