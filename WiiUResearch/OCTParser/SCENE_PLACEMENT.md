# Scene placement correction — 2026-10-23

The Grimm pieces OCT contains five geometry nodes with LocalToParentMatrix:
torso, head, armLeft, armRight, lowerBody. Each has an associated rigid body.
The nodes are flat; Asset records have AggregateCount=0. This is consistent
with a rigid break-apart piece package, not evidence of LOD alternatives.

For each node, BoundingSphereCenter + stored matrix translation reproduces
BoundingOBBCenter (within float rounding). PhysicsBody LocalToWorldMatrix
translations match those scene matrices. No manual placement offsets needed.

The reader now retains each primitive's owning scene node and transforms source
vertices by its LocalToParentMatrix before reflecting X. Missing matrices use
identity. Nested asset aggregates are explicitly unsupported when placement
is required. Nonfinite, projective, singular, and mirrored matrices are rejected.
Parent hierarchy evaluation and skeletal skinning remain future work.

Actual corrected C# OBJ export: Grimm bounds approximately
(-0.458592,-0.000794,-0.381885) to (0.458592,2.160528,0.279772).
An inspected solid-shaded projection, Parsed/grimm-assembled.png, shows an
assembled hooded figure. All 5298 vertices, 7909 triangles and 7 primitives
are retained. Freighter also retains 1068 vertices and 741 triangles.

Installed source in Documents/AssetWiiUdio/DI3MeshReader.cs; backup retained
as DI3MeshReader.before-scene-placement.cs. Full WPF Release build succeeds
with 0 errors and 17 warnings. Build: ScenePlacementBuild/AssetWiiUdio.exe.
No interactive GUI capture was made; the inspected render uses actual C# OBJ
output. Materials/textures are not applied by this mesh preview.
