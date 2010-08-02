drop table if exists entries;

create table entries (
	id integer primary key autoincrement,
	url string not null,
        experpt string not null,
        source string not null,
        updated timestamp not null,
        last_refresh timestamp not null);
        	 
