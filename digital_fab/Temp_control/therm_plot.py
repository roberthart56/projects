#Calibration of thermistor taken from microwave.
#1/16/21
#

import numpy as np
import matplotlib.pyplot as plt

temp_f = np.array([42, 69, 100, 139, 159, 171,199 ])
res = np.array([132000, 68200, 30700,12800, 8400, 6600, 4000])


temp_c = (temp_f-32)*5/9

fit_temp = temp_c[3:7]
fit_res = res[3:7]

#fit to polynomial
poly_param = np.polyfit(fit_temp, fit_res, 2)
p = np.poly1d(poly_param)
x = np.linspace(50,110,100)
z_fit= p(x)

#fig = plt.figure(figsize=(12, 8))
plt.title('Thermistor Resistance vs T(deg C)')
plt.xlabel('Temperature (C)')
plt.ylabel('R (Ohm)')
#plt.plot(temp_c, res,'ob')
plt.plot(fit_temp, fit_res, 'xr')
plt.plot(x,z_fit)
plt.show
