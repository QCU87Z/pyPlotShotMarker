import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator


#Brian
x_data = [-168,158,159,-67,-15,-46,-48,-10,-12,-127,27,-77]
y_data = [26,-19,8,-12,34,39,73,-83,47,263,157,56]
l = ["A-5","B-5","1-5","2-6","3-X","4-X","5-6","6-6","7-X","8-4","9-5","10-6"]
colours = ['red','red','blue','blue','blue','blue','blue','blue','blue','blue','blue','blue']

#284WIN 1/1
# x_data = [43,-3,-145,-138,65,80,83,-146,21,-131,-94,0]
# y_data = [-71,-162,62,117,-106,-309,-43,-78,-11,-191,-67,-42]
# l = ["A-6","B-5","1-5","2-5","3-6","4-4","5-6","6-5","7-X","8-5","9-6","10-X"]
# colours = ['red','red','blue','blue','blue','blue','blue','blue','blue','blue','blue','blue']

#300WM 2/2
# x_data = [-201,114,-88,-15,95,-91,-4,-248,-21,-9,-208,-61]
# y_data = [-30,-65,-5,-37,-111,-120,65,48,109,31,43,83]
# l = ["A-5","1-6","2-6","3-X","4-5","5-5","6-X","7-5","8-6","9-X","10-5","extra-6"]
# colours = ['red','blue','blue','blue','blue','blue','blue','blue','blue','blue','blue','red']

fig, ax = plt.subplots(figsize=(10,10))
ax.set_aspect('equal')
ax.set_xlim(-300, 300)
ax.set_ylim(-300, 300)

ringX = plt.Circle((0, 0), 127/2, color='black', fill=False, linestyle='--', linewidth=1)
ring6 = plt.Circle((0, 0), 255/2, color='black', fill=False, linewidth=1)
ring5 = plt.Circle((0, 0), 510/2, color='black', fill=False, linewidth=1)

ax.add_patch(ringX)
ax.add_patch(ring6)
ax.add_patch(ring5)

major_spacing_x = 261.8 # Major grid lines every 2 units on the x-axis
minor_spacing_x = 130.9 # Minor grid lines every 0.5 units on the x-axis

major_spacing_y = 261.8 # Major grid lines every 3 units on the y-axis
minor_spacing_y = 130.9 # Minor grid lines every 1 unit on the y-axis

# 4. Apply locators to the axes
ax.xaxis.set_major_locator(MultipleLocator(major_spacing_x))
ax.xaxis.set_minor_locator(MultipleLocator(minor_spacing_x))
ax.yaxis.set_major_locator(MultipleLocator(major_spacing_y))
ax.yaxis.set_minor_locator(MultipleLocator(minor_spacing_y))

# 5. Turn on the grid lines and customize
ax.grid(which='major', linestyle='-', linewidth='1.5', alpha=0.5, color='gray') # Customize major grid
ax.grid(which='minor', linestyle='-', linewidth='1.0', alpha=0.5, color='gray') # Customize minor grid


ax.set_title("900m - Brian\n\n29-Dec-2025")

plt.scatter(x_data, y_data, color=colours,marker='o')
for i, label in enumerate(l):
    ax.annotate(label, (x_data[i], y_data[i]), textcoords="offset points", xytext=(0,10), ha='center')

plt.grid(True, linestyle=':', alpha=0.6)
plt.axhline(0, color='gray', linewidth=0.5)
plt.axvline(0, color='gray', linewidth=0.5)

plt.show()
