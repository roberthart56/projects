


await servo_0.writeAngle(70);
await delay(200);
  

 // warning: without a powered usb-hub, currentScale > 0.5 are likely to fail 
await motor_0.setCurrent(1.5);
await motor_0.setStepsPerUnit(5);


await delay(500)

await motor_1.setCurrent(1.5);
await motor_1.setStepsPerUnit(5);


const machine = createSynchronizer([motor_0, motor_1]);

await machine.setPosition([0, 0]);

async function goto(x,y) {
  await machine.absolute([-x-y,-x+y]);
 }

var data = [[0,0],[0,10],[10,10],[10,0],[0,0]]

for (let i=0; i<5; i++){
await goto(data[i][0], data[i][1]);
await delay(100);
}


await servo_0.writeAngle(80);
  


