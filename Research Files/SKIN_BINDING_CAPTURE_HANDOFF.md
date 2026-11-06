# Scene skin-slot binding probe

Static finding: `Association::SkinInfluence` registration at 4AF0CD points to factory 4A5EE0. The loader resolves a rig matrix node from the named subnetwork/path, resolves target SceneTreeNodePool entries, and assigns that reference to each selected influence slot at call site **4A60A8**. Helper 5730E0 performs reference ownership updates and stores the node pointer. No additional transform is applied at this assignment boundary. This does not describe later GPU consumption.

Slot arithmetic observed in the loader:

```
table = sceneObject + 0x120 + u16(sceneObject + 0x12E)
entries = table + u16(table + 2)
slot = entries + influenceIndex * 4
```

New `DI3_SkinBindingLogger.lua` captures this call only when the arithmetic agrees with ECX, recording scene object, influence index, slot and rig matrix node. Subsequent Transform/Dilation matrix-return observations are accepted only when the actual scene slot still points to that output node. A fourth breakpoint captures known-prefix hand relationships for full hash identification offline. Object header bytes are raw evidence, not decoded actor/model identity.

Run script, return focus to game, press **F8 before reloading/re-entering the Elsa-only Toy Box**. Reload the Toy Box, wait for Elsa to appear, move briefly, then **F9** to save and beep. Automatic limit is 90 seconds or 1024 written records. Three observations per matrix node and relationship; loading may consume those observations, so this probe establishes binding continuity rather than a complete running animation time series. If reload exceeds the limit, the missing binding must be reported.

Output: `ce_skinbinding_*.jsonl`. Read-only hardware breakpoints, no game-data writes or forced evaluation. Mock checks pass for slot arithmetic, invalid binding rejection, later slot re-read, matrix payload widths/quotas, signature/setup failure cleanup and completion beep. Live scene binding remains untested.

Next offline checks: identify hand relationships by complete blob hashes; connect their output nodes to captured world producers and matrix nodes; compare the bound influence indices with the PC OCT associations. A name match or an object pointer by itself is insufficient to identify Elsa's renderer. Do not infer that GPU skinning consumes these slots without a further draw/update path check if that remains material.
