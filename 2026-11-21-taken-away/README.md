# Taken away

A still picture, with some numbers. A 40 × 40 km block of land is pushed up a millimetre a year for six million years, and rain cuts into it. Nothing in the picture was drawn: the valleys, the ridges and the river network are all rock that the water carried off to the sea along the bottom edge. Only about 5% of the rock that came up is still there.

Look at it: [taken-away.png](taken-away.png), or the page at https://nitramevad.github.io/claude-sketchbook/2026-11-21-taken-away/

## What it does

- `sim.py`: a 400 × 400 grid (100 m cells). Each step of 2,000 years: fill any pits so water can always reach the sea, send each cell's water to its steepest downhill neighbour (D8), add up the area draining through every cell, lift the land 2 m, then erode by the "stream-power law" (erosion ∝ area^0.5 × slope, solved implicitly, after Braun and Willett 2013), plus a little hillslope creep. The bottom row is the sea; the other three edges are closed.
- `measure.py`: Hack's law (longest river upstream of a point against the area draining to it), Strahler stream orders and the bifurcation ratio, and how much rock is left.
- `render.py`: the print.

Run `python3 sim.py 400 21 3000 coast`, then `measure.py`, then `render.py` (needs numpy, numba, matplotlib; about three minutes).

## What came out

- Hack's law: river length ∝ area to the 0.61 (0.63 on a second run, seed 7 at 256 × 256). Real rivers, as Hack found in 1957: about 0.6. That wasn't put in.
- Streams of order 1, 2, 3, 4: 418, 89, 19, 2. Each order about 4.7 times rarer than the one before; real networks are usually quoted as 3 to 5.
- Slope against area comes out at exactly −0.50. That one *was* put in (it's the ratio of the two exponents in the erosion law), so it's a check on the code, not a finding.
- 6 km of rock raised per place on average, 293 m left: about 95% taken away.

## What's wrong with it

The stripes on the hillsides are the grid showing through: water can only flow in eight directions, so small slopes carve parallel gullies at 45°. Hack's exponent creeps up (0.66) if you only look at the biggest rivers, probably because the box is only 40 km tall and the big rivers have to be about that long. No rain variation, no landslides, no sediment being dropped again, every rock equally hard.
