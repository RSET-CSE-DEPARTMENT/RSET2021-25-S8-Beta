import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Sample data structure (replace with your actual data extraction from logs)
fleet_sizes = [600, 800, 1000]
total_times = [26.92, 36.08, 44.5]  # in minutes
generation_times = {
    600: [1.45]*15,  # Replace with actual generation times
    800: [2.23]*15,
    1000: [2.54, 2.54, 2.54, 2.54, 2.54, 4.0, 2.54, 2.54, 2.54, 2.54, 2.54, 2.54, 2.54, 2.54, 2.54]
}
preprocessing_times = [2.3, 2.63, 3.83]  # in minutes
post_processing = {
    'overlap_fixing': 29,
    'schedule_analysis': 0.42
}

# Create figure and subplots
plt.figure(figsize=(18, 12))
plt.suptitle("Optimization Performance Metrics", y=1.02, fontsize=16)

# Plot 1: Total Optimization Time (Top-Left)
ax1 = plt.subplot(2, 2, 1)
bars = ax1.bar(fleet_sizes, total_times, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
ax1.set_title("Total Optimization Time (15 Generations)")
ax1.set_xlabel("Fleet Size")
ax1.set_ylabel("Time (minutes)")
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.plot(fleet_sizes, total_times, 'r--', marker='o', markersize=8)

# Plot 2: Generation Time Distribution (Top-Right)
ax2 = plt.subplot(2, 2, 2)
box_data = [generation_times[600], generation_times[800], generation_times[1000]]
box = ax2.boxplot(box_data, patch_artist=True, labels=fleet_sizes,
                 boxprops=dict(facecolor='#1f77b4', color='darkblue'),
                 medianprops=dict(color='red'))
ax2.set_title("Generation Time Distribution")
ax2.set_xlabel("Fleet Size")
ax2.set_ylabel("Time per Generation (minutes)")
ax2.grid(True, linestyle='--', alpha=0.7)

# Plot 3: Preprocessing/Initialization Time (Bottom-Left)
ax3 = plt.subplot(2, 2, 3)
ax3.plot(fleet_sizes, preprocessing_times, 'r--', marker='o', markersize=8)
ax3.bar(fleet_sizes, preprocessing_times, alpha=0.6)
ax3.set_title("Preprocessing/Initialization Time")
ax3.set_xlabel("Fleet Size")
ax3.set_ylabel("Time (minutes)")
ax3.grid(True, linestyle='--', alpha=0.7)

# Plot 4: Post-Processing Breakdown (Bottom-Right)
ax4 = plt.subplot(2, 2, 4)
components = ['Overlap Fixing', 'Schedule Analysis']
times = [post_processing['overlap_fixing'], post_processing['schedule_analysis']]
bars = ax4.bar(components, times, color=['#d62728', '#9467bd'])
ax4.set_title("Post-Processing Duration")
ax4.set_ylabel("Time (minutes)")
ax4.grid(True, linestyle='--', alpha=0.7)
for bar in bars:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f} min',
             ha='center', va='bottom')

plt.tight_layout()
plt.savefig('optimization_metrics.png', dpi=300, bbox_inches='tight')
plt.show()