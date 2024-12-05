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
(Z level 1 to -2.000)
(circular ramp)
G0 X-12.140 Y-15.275
G0 Z10.000
G1 Z0.381 F300.0
G3 X-12.170 Y-15.000 I1.240 J0.275 Z-0.004 F1000.0
G3 X-12.170 Y-15.000 I1.270 J0.000 Z-0.403
G3 X-12.170 Y-15.000 I1.270 J0.000 Z-0.803
G3 X-12.170 Y-15.000 I1.270 J0.000 Z-1.202
G3 X-12.170 Y-15.000 I1.270 J0.000 Z-1.601
G3 X-12.170 Y-15.000 I1.270 J0.000 Z-2.000
G3 X-12.170 Y-15.000 I1.270 J0.000 Z-2.000
(chip clearing - extended)
G1 X-11.853 Y-15.000 Z-0.810 F1000.0
G1 X-11.171 Y-15.000 Z-2.000 F300.0
(spiral square)
G1 X-11.298 F1000.0
G1 X-11.798 Y-15.898
G1 X-9.502 Y-16.398
G1 X-9.002 Y-13.102
G1 X-13.298 Y-12.602
G1 X-13.798 Y-17.898
G1 X-7.502 Y-18.398
G1 X-7.002 Y-11.102
G1 X-15.298 Y-10.602
G1 X-15.798 Y-19.898
G1 X-5.502 Y-20.398
G1 X-5.002 Y-9.102
G1 X-17.298 Y-8.602
G1 X-17.798 Y-21.898
G1 X-3.815 Y-22.085
G1 X-3.815 Y-7.914
G1 X-17.986 Y-7.914
G1 X-17.986 Y-22.085
G1 X-3.815 Y-22.085
(chip clearing - extended)
G1 X-4.132 Y-15.000 Z-0.810 F1000.0
G1 X-3.815 Y-8.105 Z-2.000 F300.0
(semi-adaptive north)
F1000.0
G1 Y-6.105 F1000.0
G1 X-17.986
G1 Y-8.105
G1 Z-1.873
G0 X-3.815 Y-6.168
G1 Z-2.000 F300.0
G1 Y-6.105 F1000.0
G1 Y-5.715 F1000.0
G1 X-17.986
G1 Y-6.105
(chip clearing - extended)
G1 X-10.900 Y-15.000 Z-0.810 F1000.0
G1 X-17.986 Y-21.895 Z-2.000 F300.0
(semi-adaptive south)
F1000.0
G1 Y-23.895 F1000.0
G1 X-3.815
G1 Y-21.895
G1 Z-1.873
G0 X-17.986 Y-23.831
G1 Z-2.000 F300.0
G1 Y-23.895 F1000.0
G1 Y-24.285 F1000.0
G1 X-3.815
G1 Y-23.895
G0 Z10.000
(Finish Pass)
G0 X-17.986 Y-15.000
G0 X-17.795 Y-14.682
G1 Z-2.000 F300.0
G3 X-18.113 Y-15.000 I0.000 J-0.318 F1000.0
G1 Y-24.413
G1 X-3.688
G1 Y-5.588
G1 X-18.113
G1 Y-15.000
G3 X-17.795 Y-15.318 I0.318 J0.000
G0 Z10.000
M5 (Spindle OFF)

G30 Z 10.000 (Go in Z only to preset G30 location)

G30 (Go to preset G30 location)
(</cv1>)
(----- End of Rectangular Pocket -----)

M30 (End of Program)

