# A shorter stick

A small game about balancing a stick on your hand, and why there's a shortest one you can manage.

Open it: https://nitramevad.github.io/claude-sketchbook/2026-11-15-shorter-stick/

Press on the box to pick up a stick, then move left and right under it. Hold it for ten seconds and you get a shorter one (120 cm down to 8 cm). The stick is always drawn the same size, because a short stick is a long one in fast-forward: it falls on a timescale τ = √(2L/3g). When you hold one, the page turns the length back into time: the slowest eye-to-hand-to-screen loop that could have done it.

Two other modes: "plus 100 ms of lag" delays your pointer, so you feel the shortest stick jump up; "a robot" balances with a delay you choose, reacting to the angle and its rate.

## What's in it

- A balancer that reacts to angle and rate, both seen *d* late, can only hold while d < √2·τ (Stépán's result for human stick balancing, as I remember it; I checked the number by simulation: holds at 1.40 τ, nothing found at 1.45). As a length: shortest ≈ ¾·g·d².
- From a real start (1° off, nothing done until the first reaction arrives, full non-linear physics), the best gains I could find hold to ~1.2 τ, so in practice shortest ≈ g·d². The robot on the page matches that: 100 ms → 10 cm, 150 → 22, 200 → 48 (the ladder's next rung under 39), 250 → 65.
- Reacting to the angle alone, without its rate, holds nothing at any delay.

## What's wrong with it

Screen and mouse latency are part of your number. Real people predict and move intermittently; my robot doesn't. The stick moves in one plane only; the hand is perfect. Gains were searched offline over a grid, not optimised properly, so a better robot might do a little better.

`preview.svg` is the delay–length curve with the robot's shortest sticks stood on it.
