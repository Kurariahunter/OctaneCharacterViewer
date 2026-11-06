# Run phase inspector

Open Unity menu: Tools > DI3 Static Converter > Research > Run Phase Inspector.

1. Load a cropped game reference PNG from the References folder beside this note.
2. Scrub Run cycle phase; the default baked cycle start is 1.2 seconds, after two cycles of simulated motion.
3. Adjust camera yaw, elevation, perspective and distance to approximate the reference.
4. Align feet/pelvis before judging torso, arms or dress. Previous/next buttons move one 30 Hz frame within the 0.6-second cycle.

This window previews a temporary instance of the existing PC run-plus-lean prefab. It does not modify scene objects, source clips or weights. Camera settings and phase are manual hypotheses, not recovered game parameters. It does not decode new animation channels. The two reference images are deliberately cropped game frames; they are not synchronized to the Unity phase.

Validation: isolated Unity compilation and finite-transform sampling at five times are recorded in run-phase-inspector-validation.log. Interactive rendering still requires an editor check.
