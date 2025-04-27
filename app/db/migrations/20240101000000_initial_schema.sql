-- Create projects table
create table projects (
  id text primary key,
  name text not null,
  api_key text not null unique,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now()),
  vapid_public_key text null,
  vapid_private_key text null,
  vapid_subject text null
);

-- Create devices table
create table devices (
  id bigint primary key generated always as identity,
  project_id text not null references projects(id),
  user_id text not null,
  device_id text not null,
  platform text not null,
  token text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now()),
  unique(project_id, user_id, device_id)
);

-- Create messages table (base message)
create table messages (
  id bigint primary key generated always as identity,
  project_id text not null references projects(id),
  user_id text not null,
  title text not null,
  body text not null,
  category text null,
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
