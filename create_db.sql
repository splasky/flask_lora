CREATE TABLE Devices(
    device_id TEXT PRIMARY KEY,
    abp_key TEXT NOT NULL
);

CREATE TABLE Device_Data(
    device_id TEXT,
    time DATETIME DEFAULT (datetime('now', 'localtime')),
    payload TEXT NOT NULL,
    FOREIGN KEY (device_id) REFERENCES Devices(device_id)
);
