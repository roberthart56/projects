(Mill - Rectangular Pocket G-code generated: Thu Nov 14 14:00:47 2024  <v2>)
(PathPilot Version: 2.8.3)
(Description = rectangularPocket)
(Material = Plastic : -any-)

(Units = G21 mm)
(Work Offset = G54)
(Tool Number =  4)
(Tool Description = endmill [1/8] 3FL R:0.0 loc:9.525 carbide dia:3.175 [37367])
(Tool Diameter = 3.175 mm)
(Spindle RPM = 5000)
(Flood = Off)

(Pocket Centers)
(    1  X = -10.900   Y = -15.000)

(X Width = 17.600)
(Y Height = 22.000)
(Corner Radius = 1.000)
(Feed Rate = 1000.0 mm/minute)
(Stepover = 2.000)

(Z Clear Location = 10.000)
(Z Start Location = 0.000, Z End Location = -2.000)
(Z Depth of Cut = 2.000 , Adjusted = -2.000)
(Number of Z Passes = 1)
(Z Feed Rate = 300.0mm/minute)


(----- Start of G-code -----)
(<cv1>)

G17 G90  (XY Plane, Absolute Distance Mode)
G21 (units in mm)
G54 (Set Work Offset)

G30 (Go to preset G30 location)
T4 M6 G43 H4

F 1000.0 (mm/minute)
S 5000 (RPM)
M3 (Spindle ON, Forward)


