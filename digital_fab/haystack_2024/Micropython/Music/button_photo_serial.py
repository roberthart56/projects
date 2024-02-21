import time
import machine

pin_list = ([0,7,1])    # list of input pins
N = len(pin_list)  #variable for number of inputs

inputs = ([0]*N)		#inputs

for i in range(N):
    inputs[i] = machine.Pin(pin_list[i], machine.Pin.IN, machine.Pin.PULL_UP)
inputs[2] = machine.Pin(pin_list[2], machine.Pin.IN )   #special case - no internal pull

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
