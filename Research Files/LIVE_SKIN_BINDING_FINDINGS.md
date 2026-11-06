# Skin binding capture — 2026-10-20

`ce_skinbinding_20261020_213233_165612375.jsonl` contains 576 skin binding observations across 27 scene objects, plus six hand relationship snapshots. User stopped normally with F9. Exactly one object has a complete 0–61 influence range: `0x1EC94960`. That is consistent with the 62-bone Elsa asset but is not independent actor identity proof.

There are **zero** later Transform or Dilation matrix observations whose output node matches those recorded bindings and whose scene slot still points to it. Both conversion sites did execute (4144 Transform hits and 1837 Dilation hits), so the result is a missing connection between observed conversion outputs and load-bound references, not evidence that all matrix functions stopped executing. Do not claim we have validated the rendered index matrices.

The recorded 62-slot candidate uses matrix node addresses in the 1EC... range, while captured hand relationship output nodes are in the 1EBA... range. Different address ranges alone prove nothing about rig identity; the producer/connection path must be inspected.

Direct read-only OpenProcess/ReadProcessMemory access from the command process was attempted and denied by Windows (error 5). No game memory was modified. Use the already attached Cheat Engine to obtain the small missing producer snapshot.

`DI3_ReadBoundHandProducers.lua` is a one-shot read-only script for the current scene. It checks each expected slot against the captured matrix node before dereferencing it, then records producer RTTI, vtable execute address, and bounded node/producer headers for 14 candidate hand/finger slots. It adds no breakpoints and requires no reload or hotkey. It saves `ce_sceneproducers_*.json` and beeps. Stale slots are marked instead of dereferenced. Bone names are candidates assigned by file order until association is independently verified.

Three Lua mock cases pass: matching slots, stale slots and missing attachment, including completion beep and absence of installed breakpoints. Live producer snapshot pending. The intended next step is to resolve the actual updater/connection of scene-bound matrix nodes, without repeating earlier scalar/math captures.
