import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

extent = (-3, 3, -3, 3)

delta = 1
x = np.arange(-2, 3, delta)
y = np.arange(-2, 3, delta)
X, Y = np.meshgrid(x, y)
#Z1 = np.exp(-X**2 - Y**2)
#Z2 = np.exp(-(X - 1)**2 - (Y - 1)**2)
#Z = Z1 - Z2

Z = np.array([[0, 0, 0, 0, 0],[0, 1, 3, 1, 0],[0, 4, 1, 1, 0],[0, 6, 1, 2, 0],[0, 0, 0, 0, 0]])

norm = cm.colors.Normalize(vmax=abs(Z).max(), vmin=-abs(Z).max())

fig, ax = plt.subplots()
cset1 = ax.contourf(
    X, Y, Z, 40,
    norm=norm)
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_xticks([])
ax.set_yticks([])
#fig.savefig("contour_frontpage.png", dpi=25)  # results in 160x120 px image
plt.show()
