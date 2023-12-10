// warning: without a powered usb-hub, currentScale > 0.5 are likely to fail 
await motor_0.setCurrent(1.0);
await motor_0.setStepsPerUnit(10);

await motor_1.setCurrent(1.0);
await motor_1.setStepsPerUnit(10);

const machine = createSynchronizer([motor_0, motor_1]);

machine.setPosition([0, 0]);

for (let i = 0; i < 6; i++) {
  await machine.absolute([10, 0]);
  await delay(1000);
  await machine.absolute([0, 10]);
  await delay(1000);
}


