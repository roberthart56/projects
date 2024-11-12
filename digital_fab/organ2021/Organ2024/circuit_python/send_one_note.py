import time
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

# Initialize the MIDI output over USB
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

# Define the note and velocity
note = 60  # Middle C (C4)
velocity = 64  # Medium velocity

while True:
    time.sleep(1)
    # Send a "note on" message
    print("Sending Note On")
    midi.send(NoteOn(note, velocity))

    # Wait for a moment
    time.sleep(1)

    # Send a "note off" message
    print("Sending Note Off")
    midi.send(NoteOff(note, velocity))
