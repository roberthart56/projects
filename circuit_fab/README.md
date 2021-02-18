#  Circuitboard fabrication workflow.

### Kicad notes. 

* If you want area of output to be larger than board outline, add a rectangle in the "margin" layer.  In order for that to work, the layer has to be visible when outputting svg.  It behaves differently for the silk layer, which will affect the board area even when invisible. 

* Use "export" rather than plot for export of svg.  Make sure to uncheck 'print board edges'.  Export in one file, or in separate files.  All will have the same area in the resulting svg image.

* Can use the edge cuts, fill in Inkscape, and save.  Or, to avoid the Inkscape step, make a polygon on some other layer that will not be used, such as B. Adhes.  Then export in separate files, and open directly in mods.  This seems to work.


### Inkscape notes. 

* In inkscape, you can fill a shope using the bucket icon.  I have not been able to figure out how to modify the outline that gets imported, in order to give it a fill

* Open the SVG file rather than importing.

* Make layers, and then 'save copy' with the individual parts visible.  Save as Plain SVG.  

### Mods notes.

* Had problems when I was trying to plot svg from KiCad, rather than export.  The browser crashed.  Don't do this!


