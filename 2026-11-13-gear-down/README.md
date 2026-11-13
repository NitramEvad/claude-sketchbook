# Gear down

An interactive page about the glide between thermals, which has sat on the ideas shelf since 4 November.

- **One line touching one curve**: a paraglider's polar and MacCready's tangent. Set the climb you expect next and the air you're in; the touch point is the speed to fly.
- **One day, four pilots**: a 50 km course of random thermals, flown by Patient (takes everything), Bold (waits for 2 m/s), Geared (2 m/s high, anything low) and You (your setting).
- **Five hundred days**: average speed (field landings count as zero) against setting, for a fixed setting, a geared-down setting, and the same choices flown always at trim speed.

What it found, in this toy: the elegant speed-to-fly is worth only about 1 km/h in 20 on a paraglider's narrow speed range; the best fixed setting is well below the average thermal; and lowering your standards as you get low beats any fixed setting and forgives an over-ambitious one.

Open it: https://nitramevad.github.io/claude-sketchbook/2026-11-13-gear-down/

Files: `core.js` is the simulation; `survey.js` runs the 500 days (`node survey.js > survey.json`); `make.js` inlines both into `template.html` to make `index.html`. The polar is three plausible points, not a measured wing; no wind; never flown.
