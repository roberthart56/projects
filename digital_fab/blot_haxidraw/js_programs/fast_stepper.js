// warning: without a powered usb-hub, currentScale > 0.5 are likely to fail 
await motor_0.setCurrent(1.5);
await motor_0.setStepsPerUnit(10.5);

await motor_0.setPosition(0)
await motor_0.absolute(30,700,1500)
await motor_0.absolute(0)

// for (let i = 0; i < 6; i++) {
//   await motor_0.absolute((i+1)*10)
// }

// await console.log(motor_0.getState())