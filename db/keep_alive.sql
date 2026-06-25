-- One-time setup for the Supabase Keep-Alive GitHub Action.
-- Run this once in the Supabase dashboard → SQL Editor.
--
-- The keep-alive workflow upserts row id=1 daily. A WRITE (unlike a read-only
-- SELECT) reliably registers as "sufficient activity" and prevents the free-tier
-- 7-day inactivity pause.

create table if not exists public.keep_alive (
  id        integer primary key,
  last_ping timestamptz not null default now()
);

-- Seed the row the workflow updates. Running this now also counts as activity
-- and immediately clears the current "going to be paused" warning.
insert into public.keep_alive (id, last_ping)
values (1, now())
on conflict (id) do update set last_ping = excluded.last_ping;

-- Note: the GitHub Action authenticates with the service-role key, which bypasses
-- Row Level Security, so no RLS policies are required for the upsert to succeed.
