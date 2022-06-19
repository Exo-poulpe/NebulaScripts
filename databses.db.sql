CREATE DATABASE IF NOT EXISTS vpn;
USE vpn;
CREATE TABLE IF NOT EXISTS cert (
	user_id VARCHAR(128) NOT NULL UNIQUE,
	user_fingerprint VARCHAR(128) NOT NULL,
	user_validate INT DEFAULT 1,
	PRIMARY KEY(user_id)
);
CREATE TABLE IF NOT EXISTS groups (
	group_id INT UNSIGNED NOT NULL,
	name VARCHAR(128) NOT NULL,
	PRIMARY KEY(group_id)
);
CREATE TABLE IF NOT EXISTS users (
	id_row INT UNSIGNED AUTO_INCREMENT NOT NULL,
	user_id VARCHAR(128) NOT NULL UNIQUE,
	user_pass VARCHAR(128) NOT NULL,
	user_pass_salt VARCHAR(128) NOT NULL,
	PRIMARY KEY(id_row)
);
CREATE TABLE IF NOT EXISTS groups_member (
	user_id VARCHAR(128) NOT NULL,
	group_id INT NOT NULL,
	CONSTRAINT groups_member_user
	FOREIGN KEY(user_id) REFERENCES users(user_id)
);

INSERT INTO users (user_id,user_pass,user_pass_salt)VALUES
('538c6f6f-bd69-4553-9a05-67adfee79cdc','$2b$12$J26Fzf5rpGV3SNQCq6638uMIUiAvbRYW.KvNlOhG/7mafCom/zDXG','$2b$12$J26Fzf5rpGV3SNQCq6638u'),
('31841e1a-ae71-46fc-9d78-847786148749','$2b$12$mJEAIMw7kpgRZsc46rkgpep7p0emoi2Dcrm691tWE/0g.5SGs6gea','$2b$12$mJEAIMw7kpgRZsc46rkgpe');

INSERT INTO groups (group_id,name)VALUES
('1', 'Dev'),
('2', 'Secretariat'),
('3', 'Admin'),
('4', 'Network'),
('5', 'Manager'),
('6', 'Marketing'),
('7', 'User');