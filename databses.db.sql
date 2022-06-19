BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS cert (
	user_id	TEXT NOT NULL,
	user_fingerprint	TEXT NOT NULL,
	user_validate	INT DEFAULT 1,
	PRIMARY KEY(user_id)
);
CREATE TABLE IF NOT EXISTS groups (
	group_id	INT NOT NULL,
	name	TEXT NOT NULL,
	PRIMARY KEY(group_id)
);
CREATE TABLE IF NOT EXISTS groups_member (
	user_id	INT NOT NULL,
	group_id	INT NOT NULL,
	FOREIGN KEY(user_id) REFERENCES users(user_id)
);
CREATE TABLE IF NOT EXISTS users (
	id_row	INT NOT NULL,
	user_id	TEXT NOT NULL UNIQUE,
	user_pass	TEXT NOT NULL,
	user_pass_salt	TEXT NOT NULL,
	PRIMARY KEY(id_row AUTOINCREMENT)
);
