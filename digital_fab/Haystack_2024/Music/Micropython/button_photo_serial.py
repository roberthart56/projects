import time
import machine

pin_list = ([7,0,1,2,4])    # list of input pins
N = len(pin_list)  #variable for number of inputs

inputs = ([0]*N)		#inputs

for i in range(2):    #buttons - need pullup resistors.
    inputs[i] = machine.Pin(pin_list[i], machine.Pin.IN, machine.Pin.PULL_UP)
for i in range(2,N):   #phototransistors - no pullup.
    inputs[i] = machine.Pin(pin_list[i], machine.Pin.IN )   #special case - no internal pull

tone_state = ([False]*N)

while True:
    for i in range(N):
        if (not tone_state[i]) and (not inputs[i].value()):
            print(i,'on')
            tone_state[i] = True
    
        time.sleep(0.001) #debounce.
        
        if (tone_state[i]) and (inputs[i].value()):
            print(i, 'off')
            tone_state[i] = False
            
        time.sleep(0.001) #debounce.
