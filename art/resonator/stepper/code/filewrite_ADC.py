import machine
import time

adc = machine.ADC(machine.Pin(26))  # create ADC object on ADC pin
file=open("pepe.txt","w")	# creation and opening of a CSV file in Write mode

#while True:
for i in range(10):
    value = adc.read_u16()
    file.write(str(i+1) + "," + str(value) + "\n")	# Writing data in the opened file
    print(value)
    time.sleep(0.1)

file.close()


