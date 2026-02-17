import math
import numpy as np

# Define the path to your text file
file_path = 'sbot_path002.sbp'

'''
Function def
'''

def xy_generate(width, delta_r):		#for this function, width is dist. between circle centers.
    x = np.zeros(24)
    y = np.zeros(24)
    x[1] = 0.00
    y[1] = (-delta_r)
    x[2] = width/2
    y[2] = y[1]
    
    for i, angle in enumerate(np.linspace(0.1*math.pi,math.pi,9)):
        x[i+3] = x[2]+delta_r*math.sin(angle)
        y[i+3] = -delta_r*math.cos(angle)
    
    x[12] = -width/2
    y[12] = y[11]
    
    for i, angle in enumerate(np.linspace(1.1*math.pi,2*math.pi,9)):
        x[i+13] = x[12]+delta_r*math.sin(angle)
        y[i+13] = -delta_r*math.cos(angle)
        
    x[22] = 0
    y[22] = -delta_r
    
    x[23] = 0
    x[23] = 0
   
        
    return(x,y)


#create lines
def G01(xx,yy,zz):
    return ("G01X"+f"{xx:.6f}"+"Y"+f"{yy:.6f}"+"Z"+f"{zz:.6f}")  # G01X14.1062Y4.5750Z-1.0040

'''
variable setup
'''

w = 4
r = 25.4/16/2    #radius of cutter
R = 2.2/2     #radius of pin hole.



'''
create the arrays of toolpath x,y,z

mortise depth 14 mm
mortise width 6 mm (let's make it 4 mm)
balance pin diameter 2.20 mm
make depth of cut ~1 mm, so z goes from 0 to -14 in 15 steps of  1
'''
x = np.zeros(24*15)
y = np.zeros(24*15)
z = np.zeros(24*15)

for i,d in enumerate(np.linspace(0,-14,15)):
    #replace elements in z
    z[i*24:(i+1)*24] = d* np.ones(24)   #populate z-levels
    #calculate appropriate w
    w=d*(4.0-2*R)/14+4.0    #linear relation
    #replace elements in x and y
    x_temp, y_temp = xy_generate(w-2*R, R-r)    
    x[i*24:(i+1)*24] = x_temp
    y[i*24:(i+1)*24] = y_temp
    

#change units to inches.
    
x = x/25.4 
y = y/25.4 
z = z/25.4 
    
lines_to_add = ["'(following lines are added)"]

for i in range(len(z)):
    lines_to_add.append(G01(x[i],y[i],z[i]))


#change lines below to include shopbot specific code.

lines_to_add.append("JZ,0.787402")
lines_to_add.append("'")
lines_to_add.append("'Turning router OFF")
lines_to_add.append("SO,1,0")
lines_to_add.append("J2,0.000000,0.000000")
lines_to_add.append("END")



   
#Open the file in append mode and write the new lines
with open(file_path, 'a') as file:
     for line in lines_to_add:
         file.write(line + '\n')
        
#Close the file?
 
print(f"Lines added to {file_path}")
        