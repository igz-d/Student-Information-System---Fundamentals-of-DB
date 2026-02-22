CREATE TABLE subjects( 
                        subjid INT NOT NULL, 
                        subjcode TEXT NULL DEFAULT NULL, 
                        subjdesc TEXT NULL DEFAULT NULL, 
                        subjunits INT NULL DEFAULT NULL, 
                        subjsched TEXT NULL,
                        PRIMARY KEY (subjid));

CREATE TABLE teachers( 
                        tid INT NOT NULL, 
                        tname TEXT NULL DEFAULT NULL, 
                        tdept TEXT NULL DEFAULT NULL, 
                        tadd TEXT NULL, 
                        tcontact TEXT NULL, 
                        tstatus TEXT NULL,
                        PRIMARY KEY (tid));

CREATE TABLE assign( 
                        SubjID INT NOT NULL UNIQUE, 
                        TID INT NOT NULL,
                        FOREIGN KEY (SubjID)  
                        REFERENCES subjects(subjid), 
                        FOREIGN KEY (TID) 
                        REFERENCES teachers(tid));

CREATE TABLE students( 
                         studid INT NOT NULL, 
                         studname TEXT NOT NULL, 
                         studadd TEXT NULL, 
                         studcrs TEXT NULL, 
                         studgender TEXT NULL, 
                         yrlvl TEXT NULL,
                         PRIMARY KEY (studid));

CREATE TABLE enroll( 
                         eid int NOT NULL AUTO_INCREMENT, 
                         studid INT NULL DEFAULT NULL, 
                         subjid INT NULL DEFAULT NULL, 
                         evaluation TEXT DEFAULT NULL,                 
                         PRIMARY KEY (eid), 
                         UNIQUE (studid, subjid),  
                         FOREIGN KEY (studid) 
                         REFERENCES students(studid), 
                         FOREIGN KEY (subjid) 
                         REFERENCES subjects(subjid));

CREATE TABLE grades( 
                         gradeid INT PRIMARY KEY NOT NULL AUTO_INCREMENT, 
                         enroll_eid INT UNIQUE NOT NULL, 
                         prelim TEXT NULL DEFAULT NULL, 
                         midterm TEXT NULL DEFAULT NULL, 
                         prefinal TEXT NULL DEFAULT NULL, 
                         final TEXT NULL DEFAULT NULL,                 
                         FOREIGN KEY (enroll_eid) 
                         REFERENCES enroll(eid));