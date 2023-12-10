


await servo_0.writeAngle(70);
await delay(200);
  

 // warning: without a powered usb-hub, currentScale > 0.5 are likely to fail 
await motor_0.setCurrent(1.0);
await motor_0.setStepsPerUnit(10);


await delay(500)

await motor_1.setCurrent(1.0);
await motor_1.setStepsPerUnit(10);


const machine = createSynchronizer([motor_0, motor_1]);

await machine.setPosition([0, 0]);

async function goto(x,y) {
  await machine.absolute([-x-y,-x+y]);
 }


await goto(0,10);
await delay(100);
await goto(10,10);
await delay(100);
await goto(10,0);
await delay(100);
await goto(0,0);
await delay(100);



await servo_0.writeAngle(80);
  


