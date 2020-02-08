SELECT 	s.Id AS 'Sensor Id', 
	    s.description AS 'Description', 
        sr.dateRecorded AS 'Date Recorded (UTC)', 
		sr.temperatureCelsius AS 'Temperature (Celsius)', 
		sr.temperatureCelsius * (9/5) + 32  AS 'Temperature (Fahrenheit)', 
        sr.humidity AS 'Humidity', 
        CASE sr.batterylow
			WHEN 0 THEN 'Good'
			WHEN 1 THEN 'Low' 
        END AS 'Battery Status'
from sensor s 
join sensorReading sr 
on s.id = sr.sensorId
order by s.id, sr.dateRecorded