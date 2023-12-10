await motor_0.setCurrent(1.5);
await motor_0.setStepsPerUnit(5);
//await motor_0.absolute(0,200,500);

await motor_1.setCurrent(1.5);
await motor_1.setStepsPerUnit(5);
//await motor_1.absolute(0,200,500);

const machine = createSynchronizer([motor_0, motor_1]);

await servo_0.writeAngle(60);
  

async function goto(x,y) {
  await machine.absolute([-x-y,-x+y]);
 }


for (let i=0; i<51; i++){
await goto(10*Math.sin(2*3.14*i/50), 10*Math.cos(2*3.14*i/50));
//await delay(100);
}

await servo_0.writeAngle(80);
  


