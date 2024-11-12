
#scan_matrix_play
#columns are attached to outputs, raised high,
#rows scanned with pulldown input.


import board
import time
import digitalio
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)


col_pin = [board.GP15, board.GP14, board.GP13]
row_pin = [board.GP16 ,board.GP17]

col = []		#list of configured objects for columns
row = []		#list of configured objects for rows


for pin in (col_pin):			#set up columns
    pin_obj = digitalio.DigitalInOut(pin)  #pin_obj is an internal variable
    pin_obj.direction = digitalio.Direction.OUTPUT
    col.append(pin_obj)

for pin in (row_pin):			#set up rows
    pin_obj = digitalio.DigitalInOut(pin)  
    pin_obj.direction = digitalio.Direction.INPUT
    pin_obj.pull = digitalio.Pull.DOWN
    row.append(pin_obj)
    
note = [[60, 64, 67],[72, 76, 79]]
num_rows = len(row)
num_cols = len(col)

old = [[0 for _ in range(num_cols)] for _ in range(num_rows)]

def scan_matrix(c,r):
    a=[[0 for _ in range(len(col))] for _ in range(len(row))]
    for i, el in enumerate(c):
        el.value = True
        for j, element in enumerate(r):
            a[j][i]=element.value
        el.value = False
    return(a)

while True:
    new = scan_matrix(col,row)
    for i in range(num_rows):
        for j in range(num_cols):
            if old[i][j] == False and new[i][j] == True:
                print(note[i][j], 'on')
                midi.send(NoteOn(note[i][j], 127))
            elif old[i][j] == True and new[i][j] == False:
                print(note[i][j], 'off')
                midi.send(NoteOff(note[i][j], 127))
    #time.sleep(.001)
    old = new
            
#main

