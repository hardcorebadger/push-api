-- Create projects table
create table projects (
  id text primary key,
  name text not null,
  api_key text not null unique,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- Create devices table
create table devices (
  id bigint primary key generated always as identity,
  device_id text not null,
  user_id text not null,
  platform text not null,
  token text not null,
  project_id text not null references projects(id),
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now()),
  unique(user_id, device_id, project_id)
);

-- Create user preferences table
create table preferences (
  user_id text not null,
  enabled boolean default true,
  categories text[] default array[]::text[],
  project_id text not null references projects(id),
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now()),
  primary key (user_id, project_id)
);

-- Create device preferences table
create table device_preferences (
  device_id bigint not null references devices(id),
  enabled boolean default true,
  categories text[] default array[]::text[],
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now()),
  primary key (device_id)
);

-- Create messages table (base message)
create table messages (
  id bigint primary key generated always as identity,
  user_id text not null,
  title text not null,
  body text not null,
  category text null,
  project_id text not null references projects(id),
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Create sends table (individual device deliveries)
create table sends (
  id bigint primary key generated always as identity,
  message_id bigint not null references messages(id),
  device_id bigint not null references devices(id),
  platform text not null,
  status text default 'pending',
  error text,
  delivered_at timestamp with time zone,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now()),
  unique(message_id, device_id)
); 