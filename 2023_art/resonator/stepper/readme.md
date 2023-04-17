## Steppermotor design 4/1/23

Using NEMA8 motor. Winding resistance ~8 Ohm.

Pololu driver board based on DRV8834. 

1/32 stepping, PWM at 4KHz.  ~1.2 Hz rotation.

Adjust vref on DRV chip to 0.15 V, corresponding to 0.30 A max current.  At this current, the motor runs well, and stalls with small torque.

// <img src=img/servo_driver.jpg width=50%>


###Python, accelerometer, periods, datalogging. 4/6/23

Example code for writing files.

Example code for reading and plotting files.

Result of wiggling the accelerometer.
<img src=img/file_data.png width=50%>


Checked to verify that PWM f/32/200 gives rotation frequency.

Continue on 4/10/23.  Realize that files can be overwritten as RP2040 is unpowered and repowered, starting the program again. Doh!

Now, I have a program to collect data to give me information on what to calculate to detect correct phase on resonance.  Below is a plot:

<img src=img/acc_mag.png width=50%>

4/17/23  Looked at data from 4/12.  Phase is not consistent.  Perhaps need to wait more than five minutes for transients to die.  Also possible that motor needs more current to avoid missed steps.  I changed max current to 0.58 A by adjusting VREF to 0.58V.  Run again and see if battery lasts.

<img src=img/data10_5120.png width=50%>
