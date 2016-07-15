drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  verified integer not null,
  name text not null,
  nickname text not null,
  school text not null,
  age integer not null
);
