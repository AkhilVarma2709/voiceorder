create table restaurants (
  id text primary key,
  name text not null,
  phone text,
  address text,
  active boolean default true,
  created_at timestamptz default now()
);

create table orders (
  id uuid default gen_random_uuid() primary key,
  restaurant_id text references restaurants(id),
  call_id text,
  customer_name text,
  customer_phone text,
  order_items text,
  order_total numeric,
  special_instructions text,
  pickup_confirmed boolean default false,
  call_completed boolean default false,
  call_summary text,
  status text default 'new',
  created_at timestamptz default now()
);

alter publication supabase_realtime add table orders;
create index on orders (restaurant_id, created_at desc);

insert into restaurants (id, name, phone, address)
values (
  'swadeshi-frisco',
  'Swadeshi Plaza of Frisco',
  '(469) 294-3500',
  '14300 State Hwy 121 Ste 100, Frisco, TX 75035'
);
