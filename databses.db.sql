BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "cert" (
	"user_id"	TEXT NOT NULL,
	"user_fingerprint"	TEXT NOT NULL,
	"user_validate"	INTEGER DEFAULT 1,
	PRIMARY KEY("user_id")
);
CREATE TABLE IF NOT EXISTS "groups" (
	"group_id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	PRIMARY KEY("group_id")
);
CREATE TABLE IF NOT EXISTS "groups_member" (
	"user_id"	INTEGER NOT NULL,
	"group_id"	INTEGER NOT NULL,
	FOREIGN KEY("user_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "users" (
	"id_row"	INTEGER NOT NULL,
	"user_id"	TEXT NOT NULL UNIQUE,
	"user_pass"	TEXT NOT NULL,
	"user_pass_salt"	TEXT NOT NULL,
	PRIMARY KEY("id_row" AUTOINCREMENT)
);
INSERT INTO "cert" ("user_id","user_fingerprint","user_validate") VALUES ('31841e1a-ae71-46fc-9d78-847786148749','6f7fa43848b75f4cd36121400639464d33aafced4c9f1e3f47f80aab2e7db108',1),
 ('e758dc80-15bb-4a5f-a10f-eba89be7d875','6fc878650ce55434a69b48dcf76b7487eac521746b634ecbc0de6b5b8b94e13f',1);
INSERT INTO "groups" ("group_id","name") VALUES (1,'Dev'),
 (2,'Secretariat'),
 (3,'Admin'),
 (4,'Network'),
 (5,'Manager'),
 (6,'Marketing'),
 (7,'User');
INSERT INTO "groups_member" ("user_id","group_id") VALUES ('31841e1a-ae71-46fc-9d78-847786148749',2),
 ('31841e1a-ae71-46fc-9d78-847786148749',4),
 ('e758dc80-15bb-4a5f-a10f-eba89be7d875',7),
 ('e758dc80-15bb-4a5f-a10f-eba89be7d875',5);
INSERT INTO "users" ("id_row","user_id","user_pass","user_pass_salt") VALUES (1,'31841e1a-ae71-46fc-9d78-847786148749','$2b$12$mJEAIMw7kpgRZsc46rkgpep7p0emoi2Dcrm691tWE/0g.5SGs6gea','$2b$12$mJEAIMw7kpgRZsc46rkgpe'),
 (2,'e758dc80-15bb-4a5f-a10f-eba89be7d875','$2b$12$isuDnIJjv2anRDb2w2WMpeOgX9rf.cq4F65fpux4pCbFtwBb/PxpC','$2b$12$isuDnIJjv2anRDb2w2WMpe');
COMMIT;
