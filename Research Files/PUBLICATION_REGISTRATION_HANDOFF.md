# Publication lifecycle registration — 2026-10-19

Same hash-pinned PC EXE and preferred addresses as the clock handoffs. No viewer behavior changed.

## Verified role

The only absolute pointer reference found to publication wrapper 0x6A0740 is in startup routine 0x1AA4340. Executing that complete original routine creates these callback records:

| Entry address | Existing name string | Callback |
|---|---|---|
| 0x2012EE8 | INITIALIZE | 0x6A7A10 |
| 0x2012F00 | RUN | 0x6A0740 |
| 0x2012F18 | TERMINATE | 0x6A1920 |

Each entry has a name pointer followed at +8 by four callback words. The routine writes the function address and three zeros. `validate_pc_publication_registration.py` executes original 0x1AA4340 through return, then verifies all three names and callback records. This is a native registration test, not a dispatch test.

RUN therefore reaches the previously traced chain 0x6A0740 -> 0x69F9A0 -> 0x496B00, which publishes engine clock values into typed data nodes before later calls on that path. No direct CALL references to 0x6A0740 were found; runtime dispatch through the registered callback is the lead to follow. Do not infer the callback is unused from the lack of direct calls.

## Unresolved dispatcher

An absolute-reference search found no direct code operand pointing to the RUN record itself. The registration can be reached through a larger table or enumeration. Nearby global 0x2012E90 has getter/setter and unrelated-looking lookup users; adjacency alone does not establish that it owns the lifecycle records. Those users are not accepted as dispatch evidence.

We have not established that RUN occurs once per rendered frame, on a particular thread, or immediately after 0x133EE60. The known polling loops can advance the clock separately, and prior captures showed cached controller times lagging shared clock nodes. Preserve those limitations.

## Next

Trace the containing descriptor/table and indirect dispatch of these lifecycle records, or capture bounded entry-order events at the verified clock update and RUN functions if static references remain indirect. Include thread identity and parent clock prefix in such a capture. No generic long recording is needed. This step does not yet justify changing viewer timing.

Artifacts: publication-registration-validation.json, publication_registration.txt, validate_pc_publication_registration.py.
