-- Create projects table
create table projects (
  id text primary key,
  name text not null,
  api_key text not null unique,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now()),
  vapid_public_key text,
  vapid_private_key text,
  vapid_subject text,
  fcm_credentials_json text,
  apns_key_id text,
  apns_team_id text,
  apns_bundle_id text,
  apns_private_key text
);

-- Create devices table
create table devices (
  id bigint primary key generated always as identity,
  project_id text not null references projects(id),
  user_id text,
  platform text not null,
  token text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now()),
  unique(project_id, platform, token)
);

-- Create messages table (base message)
create table messages (
  id bigint primary key generated always as identity,
  project_id text not null references projects(id),
  user_id text,
  platform text,
  device_id bigint references devices(id),
  title text not null,
  body text not null,
  icon text,
  action_url text,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables with updated_at
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_devices_updated_at
    BEFORE UPDATE ON devices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_messages_updated_at
    BEFORE UPDATE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
