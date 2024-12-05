#Version 4.  Makes toolpaths counter-clockwise.
# Define the path to your text file
# Allows a better way to enter parameters, and to save as comments to provide
# a trace of what has been done.



# 
#file_path = 'd1_r1.nc'
#pars = (-19.7, -26, 17.6, 22.0, 13.5 )
# 
#file_path = 'd1_r2.nc'
#pars = (-15.4, -86.0, 10.4, 62.0, 13.5)
#
# ************************
#
#file_path = 'd2_r1.nc'
#pars = (-19.5, -26.0, 17.6, 22.0, 12.5)
# 
# ***************************
# 
file_path = 'd3_r1.nc'
pars = (-19.2, -25.0, 17.0, 21.0, 13.5)
#
#*********************************
#
#file_path = 'd4_r1.nc'
#pars = (-19.5, -26.0, 17.6, 22.0, 13.0)
# 
# *****************************
# 
#file_path = 'd5_r1.nc'
#pars = (-19.8, -26.0, 17.6, 22.0, 13.5)
# 
#file_path = 'd5_r2.nc'
#pars = (-15.2, -71.0, 10.4, 47.0, 13.5)
# 


x_corner = pars[0]		#rectangle origin  
y_corner = pars[1]
w = pars[2]	#rectangle width  
h = pars[3]	#rectangle height  

a = min(w,h)  #rectangle minimum dimension

#toolpath parameters

d = 25.4/8    #tool diam
st = 0.8      #stepover
start_z = 0
z_safe = 3
cut_depth = 2
depth = pars[4]



#




#Calculate number of rectangular passes

N = (a/2 -d)/(d*st)   #divide half-width by pass-width
N_xy = round(N + 1.5)    #add one and round up to next integer.


#Calculate number of z - levels.
    
N_z = round((depth/cut_depth) + 0.5)  #Last cut has to be entered separately.

#Initialize lists

x = [0]*5*N_xy*(N_z)
y = [0]*5*N_xy*(N_z)
z = [0]*5*N_xy*(N_z)


x_start = x_corner + d/2	#This is coordinate for start above piece.
y_start = y_corner +d/2		#This is coordinate for start above piece.
z_start= z_safe					#Height for start.

#print(len(x))
#list x,y for first rectangular path, which is offset from rectange by d/2.

y[0] = y_start
y[1] = y[0]
y[2] = y[0] + h - d
y[3] = y[2]
y[4] = y[0]

x[0] = x_start
x[1] = x[0] + w - d
x[2] = x[1]
x[3] = x[0]
x[4] = x[0]

#create list elements for subsequent passes around rectangle.

for n in range(1, N_xy):
    y[n*5] = y[n*5-5] + st * d
    y[n*5+1] = y[n*5] 
    y[n*5+2] = y[n*5-3] - st * d
    y[n*5+3] = y[n*5+2]
    y[n*5+4] = y[n*5]
   
for n in range(1, N_xy):
    x[n*5] = x[n*5-5] + st * d
    x[n*5+1] = x[n*5-4] - st * d
    x[n*5+2] = x[n*5+1]
    x[n*5+3] = x[n*5]
    x[n*5+4] = x[n*5]

#copy this rectangular pattern for all the z - levels


for i in range(1,N_z):
    for j in range(5*N_xy):
        x[(5*N_xy*i)+j] = x[j]
        y[(5*N_xy*i)+j] = y[j]
    
    

#Create list of z's
    
for i in range(N_z-1):
    for j in range(5*N_xy):
        z[(5*N_xy*i)+j] = start_z - (i+1)* cut_depth

for j in range(5*N_xy):
    z[5*N_xy*(N_z-1)+j] = start_z - depth
    





#create lines



def G01(xx,yy,zz):
    return ("G01X"+f"{xx:.4f}"+"Y"+f"{yy:.4f}"+"Z"+f"{zz:.4f}")  # G01X14.1062Y4.5750Z-1.0040

    
#loop through z, x, and y to create list of lines to add.
lines_to_add = ["(following lines are added)"]

lines_to_add.append(G01(x_start, y_start, 3))

for i in range(len(z)):
    lines_to_add.append(G01(x[i],y[i],z[i]))
    
lines_to_add.append("G0 Z 3.00")
lines_to_add.append("M9 (All Coolant Off)")
lines_to_add.append("M5 (Spindle OFF)")
lines_to_add.append("G30 Z 10.0 (Go in Z only to preset G30 location)")
lines_to_add.append("G30 (Go to preset G30 location)")
lines_to_add.append("M30 (End of Program)")


   
#Open the file in append mode and write the new lines
with open(file_path, 'a') as file:
     for line in lines_to_add:
         file.write(line + '\n')
        
#Close the file?
 
print(f"Lines added to {file_path}")


