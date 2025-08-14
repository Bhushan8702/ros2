#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(6, 4))

# Define colors
ros2_blue = '#226699'
ros2_orange = '#FF8C00'
ros2_gray = '#444444'

# Create main circle
circle = patches.Circle((0.5, 0.5), 0.35, facecolor=ros2_blue, edgecolor='white', linewidth=3)
ax.add_patch(circle)

# Add "ROS" text
ax.text(0.5, 0.6, 'ROS', fontsize=36, fontweight='bold', 
        ha='center', va='center', color='white', family='sans-serif')

# Add "2" text
ax.text(0.5, 0.35, '2', fontsize=28, fontweight='bold', 
        ha='center', va='center', color=ros2_orange, family='sans-serif')

# Add robot-like elements (gears/cogs)
angles = np.linspace(0, 2*np.pi, 8, endpoint=False)
for i, angle in enumerate(angles):
    x = 0.5 + 0.25 * np.cos(angle)
    y = 0.5 + 0.25 * np.sin(angle)
    
    if i % 2 == 0:
        gear = patches.Circle((x, y), 0.04, facecolor=ros2_orange, alpha=0.8)
    else:
        gear = patches.RegularPolygon((x, y), 6, radius=0.03, facecolor=ros2_gray, alpha=0.6)
    ax.add_patch(gear)

# Set limits and remove axes
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect('equal')
ax.axis('off')

# Remove any whitespace
plt.tight_layout()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

# Save the logo
plt.savefig('/workspace/ros2_logo.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.close()

print("ROS2 logo created successfully!")