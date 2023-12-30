CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients(
    Username VARCHAR(256),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)

);

CREATE TABLE Appointments (
	Appointment_id INT IDENTITY,
	Name VARCHAR(255) REFERENCES Vaccines(Name),
	CUsername VARCHAR(255) REFERENCES Caregivers(Username),
	PUsername VARCHAR(256) REFERENCES Patients(Username),
	Time DATE,
	PRIMARY KEY(appointment_id)
);