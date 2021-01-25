h Machine Class stuff 2021

### Jan 15

Received Ender3.

**Build notes.**

Below are some pictures.  Top layer of box as received.  After placing uprights.  Detail of xbeam assembly.  z-limit switch placement.

![pic](./figs/box.jpg)
![pic](./figs/prights.jpg)
![pic](./figs/xbeam.jpg)
![pic](./figs/zlimit.jpg)


For the initial build, I used the instructions in the booklet that came in the box.  Took about 1.5 hours for assembly.  A build video [here](https://www.youtube.com/watch?v=me8Qrwh907Q&feature=emb_title) is very well done. I put it together first, and then watched the video. For those so  
 inclined, the build video could be followed with good results.  After the initial assembly, I found that the filament tubing did not get captured by the fitting on the extruder.  As far as I can tell, neither coupler that came with the printer works.  I ordered a set of replacements from Amazon.   [Amazon link to replacement parts](https://amzn.to/2JXDcvX)   

![pic](./figs/fittings.jpg)

These work better.  I also replaced the hot end connector with one from the Amazon package.  Both seem of better quality.
Above is a picture of the connectors received. A roll of PTFE tubing is included.  We should probably order a bunch of these, and have students build with the better fittings.  In the Creality hotend design, the PTFE tube goes all the way to the nozzle.  The tubing connector needs to work in order for there not to be a gap between tube and hot nozzle.   [Here is a video](https://www.youtube.com/watch?v=30qqKUwviww) that shows how to unclog the hot end when filament gets bunched up at the nozzle.  Below are pictures of the hot end with the shroud removed, and a filament that experienced a gap between tube and nozzle. (ie, the filament was pushed in without the tube in place!)

![pic](./figs/hotend.jpg)
![pic](./figs/hot-gap.jpg)

Once I got the machine together, and printed a first part, I took it apart and re-assembled, being more careful in places. Documents on the SD card that comes in the box also have the assembly instructions, with more details.  [Here](ender3_assy.pdf) is the pdf.
 Below are notes from both builds: 

  * Replace tubing coupler on both extruder and hot end side of PTFE tube.  
  * Tighten nuts on roller assembly, and adjust eccentric nuts to proper tension to take wobble out of plate.  This is easiest to do before assembling.   [video](https://www.youtube.com/watch?v=GsEdU8ZtI6U) gives a good explanation of these nuts.
  * Tighten plate levelling screws all the way and then back off 2-3 turns.
  * Square uprights before tightening nuts completely.
  * Adjust all rollers on extrusions before assembling.  There are three sets of these:  Two that move the z-direction, and one that moves the hotend on the x-beam.  (eccentric nuts again).
  * When placing the x-beam assembly on the vertical rails, insert the lead screw in the nut, run through its range of motion, tighten the bolts on the leadscrew nut, and back them off one turn.  Check for binding, and loosen more is needed. (suggestion from the linked build video).
  * Remove the cable ties around wire bundle to give the filament tube more freedom.  Figure out some good way to keep the cables moving freeleywithout straining connections at the hot end.  I just tied them with a rubber band to the top horizontal rail.  
  * Level the bed by moving around with the steppers off, repeatedly adjusting for distance using a sheet of paper.  
  * Bed levelling [video](https://www.youtube.com/watch?v=5eqTmb01cBk) 
  * Then preheat and load filament.  I used a gcode [linked here](./CE3_FDG_Bed_Level_190x190.gcode) that I downloaded from the link in the video below.  This code prints a nice border - can adjust the bed as it's printing.  Then it prints five pads at corners and middle.  Pictures below of before and after final adjustments.

![pic](./figs/corner001.jpg)
![pic](./figs/corners_adj.jpg)
![pic](./figs/upperleft_adj.jpg)
![pic](./figs/upperleft.jpg)

**Evaluation and comments.**

* The x motion of the hot end has a bit of a bump every ~70 mm, consistent with a bad place on a roller.  

* Below is a picture of a test print: [Freecad file](./overhang_test.FCStd) and [stl file](./overhang.stl), printed with the same PLA filament on the Ender-3 and on a PRUSA MK3S. The Ender print is perhaps a little better than PRUSA's. 

![pic](./figs/comparison.jpg)
