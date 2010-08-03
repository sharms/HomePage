drop table if exists entries;

create table entries (
	id integer primary key autoincrement,
	url string not null,
        image_url string not null,
        excerpt string not null,
        source string not null,
        updated timestamp not null,
        last_refresh timestamp not null);
        	 
