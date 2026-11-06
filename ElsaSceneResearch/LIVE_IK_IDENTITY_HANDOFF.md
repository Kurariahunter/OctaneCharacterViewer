# Live IK replay and unresolved instance association

2026-10-17. Capture octane_20261017_000852_1792210132334652700.json.60samples, complete scan,zero failed chunks,4IK candidates, no IK candidate-limit truncation.

## Replay result

Two candidates have changing targets/twists. Replaying all13recorded inputs through the pinned original native routine0x53b620 reproduces captured outputs closely across60samples each:
-0x1e2376ec:maxcomponent1.67787075e-5,maxrotation0.00202278degrees.
-0x1e2377f0:maxcomponent0.0001468360,maxrotation0.01762081degrees.

This supports the captured native IK input/output layout and solver replay. Non-atomic reads limit exact equality. Two other candidates have zero targets and static outputs.

## Important identity boundary

Changing IK candidates refer to network0xd1bfc80; updating hair/dress chains refer to0xcbe6c80. Neither IK candidate matches the exact initial-geometry signature of source Elsa processors408/412. Thus actor/source association is UNRESOLVED. They may be another rig or a related driver network; do not treat them as Elsa's solver or apply their twist values to Elsa. The changing twist ranges[-0.1316731,0] and[0,0.00651134] are recorded observations only.

## Direct thigh path now found

The deeper skirt trace reaches source-shaped thigh proxy Dilation nodes0x1e073118/0x1e073300. Their tagged Orientation inputs are0x1e0732bc/0x1e0734a4, with producer execute0x4c83f0. Captured producer headers contain input pointers0x1e06f740/0x1e06ec84. Original disassembly proves this is a typed quaternion copy: Input atproducer+18,Output+1c. Its output must alias the requested node before following the input. Those input node payloads/producer headers were beyond the previous recognized boundary and cannot be recovered from this capture alone.

Reader updated for0x4c83f0 typed connection and previously native-validated0x4d2370 inverse chain. Synthetic output-alias tests pass; deeper existing14level/1024nodebounds preserved. Next capture should expose the producer actually feeding Elsa-shaped thigh proxies, independently of the broad IK scan. New live traversal remains unverified until capture. No game-memory writes, mesh/weights or preview changes.

Reproduction: validate_live_ik_replay.py -> live-ik-replay-validation.json. The script explicitly reports shares_updating_chain_network=false and no exact initial geometry matches. First draft selected only shared networks and found none; changing-target candidates were then replayed without claiming association.
