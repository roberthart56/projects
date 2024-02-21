from bit_operations import get_x_y, clear_x_y, set_x_y
    
#buffer = bytearray([0xff] * 128)
# width = 32
# height = 32
# buflen = width*height//8

# buffer = bytearray([0b01010101] * buflen)

def update_array(array, w, h):
    output_array = bytearray([0x00] * len(array))
    for x in range(0,w):			#toroidal BC use all pixels
        for y in range(0,h):			#toroidal BC use all pixels
            sum = 0
            for i in range (-1,2):
                for j in range(-1,2):
                    sum += get_x_y(array, w, (x+i)%w, (y+j)%h) #This line allows wraparound for toroid.   
            #print(sum)
            
            if sum == 3:			#next generation is alive
                set_x_y(output_array, w, x, y)
            elif sum == 4:			#next generation does not change
                if get_x_y(array, w, x, y):
                    set_x_y(output_array, w, x, y)
                else:
                    clear_x_y(output_array, w, x, y)
            else:							#next generation not alivebiffer
            
                clear_x_y(output_array, w, x, y)
    return(output_array)
            
            
#buffer = update_array(buffer, width, height)