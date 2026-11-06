# Original leg IK routine running

Native routine0x53b620 executed in isolated32-bit x86 emulation, with verified original executable SHA256 recorded in leg-ik-native-validation.json. No game process launched. This is execution of recovered code, not a clean portable reimplementation.

Registration0x50211b -> factory0x54b880 -> wrapper0x54b850 -> allocator/config0x545f40. RTTI vtable0x1b343ec. Factory assigns input/output slots by names, not authored DataNodeRefs order. Source ordered input indices must be reordered [12,2,1,10,3,8,9,7,6,5,4,0,11]. Internal outputs reordered [1,0,3,2] to authored mid rotation/start rotation/mid scale/start scale.

Both Elsa processor NetworkBuffer words are23. Factory maps these to runtimeflags30: scale enable4, squash option8, secondary option16, axis selector2. More detailed semantic names remain tentative; the bit mapping is traced, not guessed. Processor input count13 and output count4.

200 deterministic reachable-target tests across both authored leg geometries. Fixed zero pole/twist and unit input scale. Original quaternions remain unit; scales remain1; forward kinematics reaches target within max1.511e-5 model units. Initial-target rotation comparison matches stored graph rotation matrices within2.257e-6. Test tolerance5e-5 allows measured original-routine numerical error; this is not exact algebraic fidelity. Unreachable targets, squash edge cases, other flag combinations and arbitrary rig shapes are unvalidated.

Controlled four-second bend demo uses synthetic ankle trajectories. It does NOT decode Elsa's original animation targets. NativeLegIK.prefab is a separate stick-leg demonstration, not the character idle. Orange target/cyan solved ankle should overlap. Never label these as recovered original clips.

Original motion target graph remains blocked by RelationshipProcessor nodes24/34, which map foot/ball/toe controls into multiple transforms. Other basis conversions remain undecoded. Multi-output discovery now recognizes all Output-prefixed names; unsupported Relationship and IK processors fail before following output dependencies, avoiding fake self-cycles or silently using stored output defaults. No native IK injected into production evaluator yet.

Next: trace foot RelationshipProcessor, reproduce authored foot control outputs, then validate all required basis conversions and missing upper-leg skin composition before claiming planted feet in Elsa's animation.
