## Steppermotor design 4/1/23

Using NEMA8 motor. Winding resistance ~8 Ohm.

Pololu driver board based on DRV8834. 

1/32 stepping, PWM at 4KHz.  ~1.2 Hz rotation.

Adjust vref on DRV chip to 0.15 V, corresponding to 0.30 A max current.  At this current, the motor runs well, and stalls with small torque.

// <img src=img/servo_driver.jpg width=50%>





