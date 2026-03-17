-- Schema for Hostel Management (MySQL-compatible DDL)
CREATE DATABASE IF NOT EXISTS hostel_db;
USE hostel_db;

-- 1. Student
CREATE TABLE IF NOT EXISTS Student (
    Student_ID VARCHAR(32) PRIMARY KEY,
    Name VARCHAR(200),
    Gender VARCHAR(16),
    Phone VARCHAR(32),
    Email VARCHAR(200),
    Address TEXT,
    Password VARCHAR(255),
    Course VARCHAR(100)
);

-- 2. Hostel
CREATE TABLE IF NOT EXISTS Hostel (
    Hostel_ID VARCHAR(32) PRIMARY KEY,
    Hostel_Name VARCHAR(200),
    Location VARCHAR(200),
    Type VARCHAR(16) -- Boys/Girls
);

-- 3. Room
CREATE TABLE IF NOT EXISTS Room (
    Room_ID VARCHAR(32) PRIMARY KEY,
    Room_Number VARCHAR(32),
    Room_Type VARCHAR(64),
    Capacity INT,
    Hostel_ID VARCHAR(32),
    FOREIGN KEY (Hostel_ID) REFERENCES Hostel(Hostel_ID)
);

-- 4. Allocation
CREATE TABLE IF NOT EXISTS Allocation (
    Allocation_ID VARCHAR(32) PRIMARY KEY,
    Student_ID VARCHAR(32),
    Room_ID VARCHAR(32),
    Allotment_Date DATE,
    FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
    FOREIGN KEY (Room_ID) REFERENCES Room(Room_ID)
);

-- 5. Fees
CREATE TABLE IF NOT EXISTS Fees (
    Fee_ID VARCHAR(32) PRIMARY KEY,
    Student_ID VARCHAR(32),
    Amount DECIMAL(10,2),
    Payment_Date DATE,
    Payment_Status VARCHAR(32),
    FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID)
);

-- 6. Warden
CREATE TABLE IF NOT EXISTS Warden (
    Warden_ID VARCHAR(32) PRIMARY KEY,
    Name VARCHAR(200),
    Phone VARCHAR(32),
    Hostel_ID VARCHAR(32),
    FOREIGN KEY (Hostel_ID) REFERENCES Hostel(Hostel_ID)
);

-- 7. Leave
CREATE TABLE IF NOT EXISTS Student_Leave (
    Leave_ID VARCHAR(32) PRIMARY KEY,
    Student_ID VARCHAR(32),
    Leave_Date DATE,
    Return_Date DATE,
    Reason TEXT,
    FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID)
);

-- 8. Laundry
CREATE TABLE IF NOT EXISTS Laundry (
    Laundry_ID VARCHAR(32) PRIMARY KEY,
    Student_ID VARCHAR(32),
    Clothes_Count INT,
    Laundry_Date DATE,
    Charges DECIMAL(10,2),
    Status VARCHAR(32),
    FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID)
);

-- 9. Complaint
CREATE TABLE IF NOT EXISTS Complaint (
    Complaint_ID VARCHAR(32) PRIMARY KEY,
    Student_ID VARCHAR(32),
    Room_ID VARCHAR(32),
    Complaint_Date DATE,
    Complaint_Type VARCHAR(100),
    Description TEXT,
    Status VARCHAR(32),
    FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
    FOREIGN KEY (Room_ID) REFERENCES Room(Room_ID)
);

-- 10. Maintenance
CREATE TABLE IF NOT EXISTS Maintenance (
    Maintenance_ID VARCHAR(32) PRIMARY KEY,
    Complaint_ID VARCHAR(32),
    Hostel_ID VARCHAR(32),
    Maintenance_Date DATE,
    Work_Type VARCHAR(200),
    Cost DECIMAL(10,2),
    Status VARCHAR(32),
    FOREIGN KEY (Complaint_ID) REFERENCES Complaint(Complaint_ID),
    FOREIGN KEY (Hostel_ID) REFERENCES Hostel(Hostel_ID)
);

-- Sample test data for local development
INSERT INTO Student (Student_ID, Name, Gender, Phone, Email, Address, Password, Course)
VALUES ('STU101', 'Test Student', 'M', '+911234567890', 'test@student.local', '123 College Rd', 'pass123', 'BSc Computer Science')
ON DUPLICATE KEY UPDATE Name=Name;

INSERT INTO Hostel (Hostel_ID, Hostel_Name, Location, Type)
VALUES ('H01','Boys Alpha','North Campus','Boys')
ON DUPLICATE KEY UPDATE Hostel_Name=Hostel_Name;

INSERT INTO Room (Room_ID, Room_Number, Room_Type, Capacity, Hostel_ID)
VALUES ('R001','B-203','3-Seater',3,'H01')
ON DUPLICATE KEY UPDATE Room_Number=Room_Number;

INSERT INTO Warden (Warden_ID, Name, Phone, Hostel_ID)
VALUES ('WRD501','Test Warden','+911112223334','H01')
ON DUPLICATE KEY UPDATE Name=Name;