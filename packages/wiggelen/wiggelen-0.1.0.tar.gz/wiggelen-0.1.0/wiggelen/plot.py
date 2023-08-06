#!/usr/bin/env python

import sys
import matplotlib.pyplot as plt
import wiggelen


GENOME_SIZE = 16569
RESOLUTION = int(sys.argv[2]) if len(sys.argv) > 2 else 100

positions = []
values = []


def downscale(walker, resolution):
    previous_position = -resolution
    for chrom, position, value in walker:
        if position >= previous_position + resolution:
            previous_position = position
            yield chrom, position, value


for _, position, value in downscale(wiggelen.walk(open(sys.argv[1])), RESOLUTION):
    positions.append(position)
    values.append(value)


plt.plot(positions, values, linewidth=1.0)
plt.axis([1, GENOME_SIZE, min(values), max(values)])

plt.xlabel('mitochondrial genome')
plt.ylabel('value')
plt.title('Wiggle track')
#plt.grid(True)
plt.show()
