BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "demande" (
	"id_demande"	INTEGER,
	"id_user"	INTEGER NOT NULL,
	"date_demande"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	"politiques"	TEXT NOT NULL,
	"etat"	VARCHAR(20) DEFAULT 'En attente',
	"id_dossier"	INTEGER NOT NULL,
	PRIMARY KEY("id_demande" AUTOINCREMENT),
	FOREIGN KEY("id_dossier") REFERENCES "dossier_medical"("id_dossier"),
	FOREIGN KEY("id_user") REFERENCES "user"("iduser")
);
CREATE TABLE IF NOT EXISTS "dossier_medical" (
	"id_dossier"	INTEGER,
	"id_patient"	INTEGER NOT NULL,
	"date_creation"	DATE NOT NULL,
	"pathologies"	TEXT,
	"traitements"	TEXT,
	"allergies"	TEXT,
	"antecedents"	TEXT,
	"observations"	TEXT,
	"date_derniere_modification"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id_dossier"),
	FOREIGN KEY("id_patient") REFERENCES "user"("iduser")
);
CREATE TABLE IF NOT EXISTS "role" (
	"idrole"	int(11) NOT NULL,
	"rolename"	varchar(255) DEFAULT NULL
);
CREATE TABLE IF NOT EXISTS "user" (
	"iduser"	INTEGER,
	"mail"	TEXT DEFAULT NULL,
	"motdepasse"	TEXT DEFAULT NULL,
	"nom"	TEXT DEFAULT NULL,
	"prenom"	TEXT DEFAULT NULL,
	"role_id"	INTEGER NOT NULL,
	"date_naissance"	TEXT,
	PRIMARY KEY("iduser"),
	FOREIGN KEY("role_id") REFERENCES "role"("idrole")
);
CREATE TABLE IF NOT EXISTS "user_dossier" (
	"id_user"	INTEGER NOT NULL,
	"id_dossier"	INTEGER NOT NULL,
	"nom_privilege"	VARCHAR(20) NOT NULL,
	PRIMARY KEY("id_user","id_dossier"),
	FOREIGN KEY("id_dossier") REFERENCES "dossier_medical_old"("id_dossier"),
	FOREIGN KEY("id_user") REFERENCES "user"("iduser")
);
INSERT INTO "demande" VALUES (1,15,'2025-01-03 16:57:48','Politique de confidentialité','En attente',1);
INSERT INTO "demande" VALUES (2,15,'2025-01-03 17:00:12','Lire , Ecrire','En attente',1);
INSERT INTO "dossier_medical" VALUES (1,16,'2025-01-02','test	','test','test','test','test','2025-01-02 13:53:31');
INSERT INTO "dossier_medical" VALUES (2,13,'2025-01-03','Diabète, Hypertension','Insuline, Médicaments antihypertenseurs','Aucune','Pas dantécédents familiaux','Observation du patient: stable','2025-01-03 17:14:04');
INSERT INTO "role" VALUES (1,'admin');
INSERT INTO "role" VALUES (2,'medecin traitant');
INSERT INTO "role" VALUES (3,'medecin consultant');
INSERT INTO "role" VALUES (4,'infirmier');
INSERT INTO "role" VALUES (5,'patient');
INSERT INTO "user" VALUES (6,'maroua@example.xom',X'674141414141426e474c565844625878783372756b486b524a436b727230684a7839457a41732d736c5a7536476b6e706f6e4f7765424a7173724d6572736b42754d78355f376663574c647543705967705833766772367a47566b696646424a78413d3d','chelabi','maroua',1,NULL);
INSERT INTO "user" VALUES (10,'nacer@example.xom',X'674141414141426e4944537652746b57705f336d6c6231575f793379324938525a70545f644c77574d4e576d637279354d67776b656578363836573555485f3657525956496830725670426b646c6e6e55356446657043394d6e3572483938634d673d3d','Nacer','Benrais',2,NULL);
INSERT INTO "user" VALUES (11,'inesboudraa@gmail.com',X'674141414141426e4b7174766f4b4f364c387263562d58687547622d4b39326a386a47424770665f36477270497951435f5f6564706c4a742d5261543552343578616e4147474c7750344875594f6e35726d394f6e37373071795f39424c367252785f786968787a5577795a5f64366e68714930416e453d','Boudraa','Ines Yasmine',4,NULL);
INSERT INTO "user" VALUES (12,'test@test.com',X'674141414141426e4b304b55676d5159666659505a2d66614d64623159336672363271784f765f7a37596457586e43693376556c394a4f4c6841366f6364584f4f41624a6b675668626f4742392d5439656266476465634c33417869554f6a696d413d3d','test','test',3,NULL);
INSERT INTO "user" VALUES (13,'t@t.com',X'674141414141426e4b31373148475a4275556c784a4762747751384137344d723670426a5a4f4d37353442484e324e5f4377527a7a526f676f65774d4c64514a62774d38487773337441756f6a72504e34594b734c4664566a38326c644842695f413d3d','boudraaaaa','inesss',5,NULL);
INSERT INTO "user" VALUES (14,'tetete@example.com',X'674141414141426e4b324c54586c626b46686b5932524f54326841634b4c39697264514a4730795a5f4171375753666247765066784639655a6a4e576a4c555f6b6f4765366a6b43475a4c474d457267683653415775524734434a384e7a4f464e747a6646564334684171544868354930312d6232336f3d','teset','tese',5,'2005-05-06');
INSERT INTO "user" VALUES (15,'Maroua@example.com',X'674141414141426e4b327066335743446130476b526841455537467867486a51595139386f4644773134314d6d3769485a475a76464156424732544a30496b4c79556e613965575530446569757051692d53786a425754585438725733354552436234306b4d4647424c3773375f4c524a7075733248513d','Chelabi','Maroua',1,'2003-07-27');
INSERT INTO "user" VALUES (16,'Hadil@gmail.com',X'674141414141426e636254687a477953427359484371516a65666a615751474c6667455a76594d57544f395f63754c50495845576c5650476e4c666a676e7259576e386658514269415a434f2d633944436166427532616732496c36486a65674c513d3d','Hadil','Hadil',2,'2003-07-27');
INSERT INTO "user_dossier" VALUES (15,2,'owner');
COMMIT;