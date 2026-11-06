# PC downstream dress Transform capture tool

2026-10-17. Implementation complete; live local/world path validation pending the next capture.

## Run

Use F:/DisneyInfinityPortalTest/OctaneLiveInspector/Capture Dress Skin Transforms.cmd with the installed PC game and Elsa active. Return to the game during the five-second delay, then keep her moving/turning without changing scenes for about90seconds while the bounded scans/capture finish. The command uses the existing read-only inspector, adds --dress-skin, retains --dress-dynamics, and requests240samples at5ms intervals with one expensive upstream/IK context. Actual sampling can be slower.

Send the full generated JSON or its matching dynamics summary. Files save in OctaneLiveInspector/Captures. The summary now includes downstream path count, discovery boundaries and per-chain error/completed-frame/matching-dynamics counts. Existing commands retain their behavior.

## Discovery

Source PC graph: local dress Transform697/713 composes Orientation689/705 and Translation695/711. World Transform699/715 concatenates that local Transform with the corresponding chain anchor643/649. Native routines: compose0x5303e0, world concatenate0x57e240, Aim0x534380.

The new dress_skin_capture.py discovers compose/concatenate vtable candidates from the hash-pinned executable's PE sections, verifies live execute entries, then scans readable private memory with a30second bound and4096record limit. Static audit found compose vtable0x1b3514c and concatenate vtables0x1b2ee44/0x1b38b9c. These static signatures are confirmed; the live downstream layout has not yet been demonstrated.

Every accepted processor must have bounded recognized layout and an output node whose producer points back to it. A local compose must consume the chain's cached orientation as an input-tagged component; a world concatenate must consume that exact local aggregate followed by the exact chain anchor. Multiple matching paths are reported as ambiguous and rejected. Named actor ownership is not inferred. A unique source-shaped path is graph evidence, not proof of the renderer consuming that node.

## Sampling

Each sample revalidates the processor links and cached orientation's known Aim execute/output alias. It captures node headers and exact numeric payload bytes for local/world Transform16, anchor Transform16, quaternion4, present translation/scale/unscale components, and particle positions. Invalid/nonfinite/unreadable fields produce explicit errors.

Independent global-frame/native-last-frame stamps bracket the downstream reads. completed_frame requires unchanged stamps and equality of global/native frames. matches_dynamics_frame additionally requires equality with that chain's separate dynamics capture stamp pair. These filters are necessary comparison qualifications and do not prove atomicity. Header and payload reads can still race.

Captured16-float Transform payloads are quaternion/translation/uniform/Scale4/Unscale4, NOT a flat4x4matrix. The final Matrix4x4variant node is not discovered in this increment. The world Transform is the source skin-path input to that conversion; after live validation it can be independently converted to a matrix using verified native point/transform operations. Do not report final skin matrices captured or final mesh parity established yet.

## Validation and next comparison

Synthetic tests pass for discovery scan, exact links, output aliases, missing input tags, duplicate path rejection, stale anchors, mid-read stamp changes, Aim output alias, finite/readable payloads and summary counts. Existing dynamics, upstream,13/4IK and PC8/3IK tests pass. CLI help exposes the new flag, which requires --dress-dynamics. Static vtable audit saved at pc-dress-skin-vtable-audit.json.

No process write API, injection, hook, debugger attachment or pause was added. No Unity assets or game installation files changed. Live execution is still required to establish whether the compose/world producer layouts match. Next compare captured local Transform to native inverse root-position + carried Aim, and world Transform to native local/anchor concatenation on completed matching-frame snapshots.
