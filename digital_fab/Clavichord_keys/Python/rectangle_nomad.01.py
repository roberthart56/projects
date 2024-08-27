# Define the path to your text file
file_path = 'nomad_head.txt'

w = 5	#rectangle width
h = 25	#rectangle height
a = min(w,h)  #rectangle minimum dimension

#toolpath parameters

d = 3   #25.4/8    #tool diam
st = 0.8      #stepover
start_z = 0
cut_depth = 1
depth = 2.9


x_corner = 3		#rectangle origin
y_corner = 3	




#Calculate number of rectangular passes

N = (a/2 -d)/(d*st)   #divide half-width by pass-width
N_xy = round(N + 1.5)    #add one and round up to next integer.


#Calculate number of z - levels.
    
N_z = round((depth/cut_depth) + 0.5)  #Last cut has to be entered separately.

#Initialize lists

x = [0]*(5*N_xy*(N_z) + 1)
y = [0]*(5*N_xy*(N_z) + 1)
z = [0]*(5*N_xy*(N_z) + 1)


x[0] = x_corner + d/2	#This is coordinate for start above piece.
y[0] = y_corner +d/2		#This is coordinate for start above piece.
z[0] = 3					#Height for start.

#print(len(x))
#list x,y for first rectangular path, which is offset from rectange by d/2.

x[1] = x[0]
x[2] = x[1]
x[3] = x[1] + w - d
x[4] = x[3]
x[5] = x[1]

y[1] = y[0]
y[2] = y[1] + h - d
y[3] = y[2]
y[4] = y[1]
y[5] = y[1]

#create list elements for subsequent passes around rectangle.

for n in range(1, N_xy):
   x[n*5+1] = x[n*5-4] + st * d
   x[n*5+2] = x[n*5+1] 
   x[n*5+3] = x[n*5-2] - st * d
   x[n*5+4] = x[n*5+3]
   x[n*5+5] = x[n*5+1]
   
for n in range(1, N_xy):
   y[n*5+1] = x[n*5-4] + st * d
   y[n*5+2] = x[n*5-3] - st * d
   y[n*5+3] = x[n*5+2]
   y[n*5+4] = x[n*5+1]
   y[n*5+5] = x[n*5+1]

#copy this rectangular pattern for all the z - levels


for i in range(1,N_z):
    for j in range(5*N_xy):
        x[(5*N_xy*i+1)+j] = x[1+j]
        y[(5*N_xy*i+1)+j] = y[1+j]
    
    

#Create list of z's
    
for i in range(N_z-1):
    for j in range(5*N_xy):
        z[(5*N_xy*i+1)+j] = start_z - (i+1)* cut_depth

for j in range(5*N_xy):
    z[5*N_xy*(N_z-1)+1+j] = start_z - depth
    





#create lines



def G01(xx,yy,zz):
    return ("G01X"+f"{xx:.4f}"+"Y"+f"{yy:.4f}"+"Z"+f"{zz:.4f}")  # G01X14.1062Y4.5750Z-1.0040

    
#loop through z, x, and y to create list of lines to add.
lines_to_add = ["(following lines are added)"]

for i in range(len(z)):
    lines_to_add.append(G01(x[i],y[i],z[i]))

lines_to_add.append("G00Z3.0000")
lines_to_add.append("G00X0.0000Y0.0000Z3.0000")
lines_to_add.append("M05")
lines_to_add.append("M30")
lines_to_add.append("%")





   
#Open the file in append mode and write the new lines
with open(file_path, 'a') as file:
     for line in lines_to_add:
         file.write(line + '\n')
        
#Close the file?
 
print(f"Lines added to {file_path}")
