CREATE TABLE ConfigTbl (
	configName VARCHAR(100),
	configValue INT
);

INSERT INTO ConfigTbl(configName, configValue)
	VALUES ('CurrentSound', NULL);
INSERT INTO ConfigTbl(configName, configValue)
	VALUES ('MaxSoundLength', 30);
INSERT INTO ConfigTbl(configName, configValue)
	VALUES ('Volume', 50);

CREATE TABLE SoundLibraryTbl (
	soundId INT PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	description VARCHAR(2000),
	length INT NOT NULL,
	file BYTEA NOT NULL,
	uploadTime TIMESTAMP NOT NULL
);
