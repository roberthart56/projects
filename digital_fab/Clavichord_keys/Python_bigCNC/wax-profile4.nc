(Mill - Rectangular Profile G-code generated: Fri Apr  7 14:20:24 2023  <v1>)
(PathPilot Version: 2.8.3)
(Description = rectangularProfile)
(Material = Plastic : -any-)

(Units = G21 mm)
(Work Offset = G54)
(Tool Number =  1)
(Tool Description = endmill [3/8] 3FL R:0.0 loc:25.4. carbide dia:9.525 [37373])
(Tool Diameter = 9.525 mm)
(Spindle RPM = 2000)
(Flood = On)

(Feed = 1500.0 mm/minute)
(Stepover = 3.000)

(--- Perimeter Locations ---)
(X Start Location = 0.000, X End Location = 94.000)
(Y Start Location = 0.000, Y End Location = -73.000)

(--- Rectangular Profile Locations ---)
(X Profile Start Location = 0.000, End Location = 94.000)
(Y Profile Start Location = 0.000, End Location = -73.000)
(Corner Radius = 2.5)

(Z Clear Location = 10.000)
(Z Start Location = 0.000 , End Location = -17.000)
(Z Depth of Cut = 17.000 , Adjusted = 17.000)
(Number of Z Passes = 1, direction = -1)
(Z Feed Rate = 750.0 mm/minute)


(----- Start of G-code -----)
(<cv1>)

G17 G90  (XY Plane, Absolute Distance Mode)
G64 P 0.130 Q 0.000 (Path Blending)
G21 (units in mm)
G54 (Set Work Offset)

G30 (Go to preset G30 location)
T1 M6 G43 H1

F 1500.0 (Feed, mm/minute)
S 2000 (RPM)

M8 (Flood Coolant ON)
M3 (Spindle ON, Forward)
(Finish Pass - Z Level 1)
G0 X 98.763 Y 4.762
G0 Z 10.000
G0 X 98.763 Y 4.762 
G1 Z -17.000 F 750.0
G1 X 98.763 Y -70.500  F 1500.0 
G2 X 91.500 Y -77.763  I -7.262 J 0.000 
G1 X 2.500 Y -77.763 
G2 X -4.762 Y -70.500  I 0.000 J 7.262 
G1 X -4.762 Y -2.500 
G2 X 2.500 Y 4.762  I 7.262 J 0.000 
G1 X 91.500 Y 4.762 
G2 X 98.763 Y -2.500  I 0.000 J -7.262 
G0 Z 10.000 

M9 (All Coolant Off)
M5 (Spindle OFF)

G30 Z 10.0 (Go in Z only to preset G30 location)

G30 (Go to preset G30 location)
(</cv1>)
(----- End of Rectangular Profile -----)

M30 (End of Program)

