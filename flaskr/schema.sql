DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS matches1;
DROP TABLE IF EXISTS matches2;

CREATE TABLE players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL UNIQUE,
	picture	TEXT NOT NULL,
	bp INTEGER NOT NULL,
    elo INTEGER NOT NULL
);

CREATE TABLE events (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	url TEXT NOT NULL UNIQUE,
	title TEXT NOT NULL UNIQUE,
	participants TEXT NOT NULL,
	teamsize INTEGER NOT NULL,
	rankings TEXT
);

CREATE TABLE matches1 (
	title TEXT NOT NULL,
	winner TEXT NOT NULL,
	loser TEXT NOT NULL,


	winnerscore INTEGER NOT NULL,
	loserscore INTEGER NOT NULL,
	tournament INTEGER NOT NULL,

    FOREIGN KEY (winner) REFERENCES players (name),
    FOREIGN KEY (loser) REFERENCES players (name)
);

CREATE TABLE matches2 (
	title TEXT NOT NULL,
	winner1	TEXT NOT NULL,
	winner2	TEXT NOT NULL,
	loser1	TEXT NOT NULL,
	loser2	TEXT NOT NULL,

	winnerscore INTEGER NOT NULL,
	loserscore INTEGER NOT NULL,
	tournament INTEGER NOT NULL,

    FOREIGN KEY(winner1) REFERENCES user (name),
    FOREIGN KEY(winner2) REFERENCES user (name),
    FOREIGN KEY(loser1) REFERENCES user (name),
    FOREIGN KEY(loser2) REFERENCES user (name)
);
