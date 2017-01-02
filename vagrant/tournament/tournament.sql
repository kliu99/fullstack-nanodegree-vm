-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


CREATE TABLE players ( 
	id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE matches ( 
	host INTEGER REFERENCES players (id),
	guest INTEGER REFERENCES players (id),
	winner INTEGER REFERENCES players (id),
	PRIMARY KEY (host, guest)
);


CREATE VIEW match_players AS SELECT host, guest FROM matches


