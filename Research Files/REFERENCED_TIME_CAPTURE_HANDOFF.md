# Referenced-track sample time and buffer probe — 2026-10-19

New script: OctaneLiveInspector/CheatEngine/DI3_ReferencedTimeLogger.lua. Two hardware execute breakpoints, no injected instructions, game writes or forced evaluation:

1.59EB40 sampler entry: ECX ReferencedTrack, stack+4 timefloat,stack+8 destination pointer,returncaller. Track+28 asset -> asset+3C sourceClipDataBlock. Captures sourceprefix256,trackheader80 and source mapping header64 fromtrack+2C. Only exact ReferencedTrack RTTI candidate accepted.
2.5A1611 after child evaluation and before group clip-buffer dispatch: ESIchild,ECXmanager,stack weight/mode/filter. Native5A00D0 confirms managerdepth at+0,table+8,16byteframe stride,source pointer frame+4,rowcount frame+8,52byte rowstride(mask at+30). Captures source rows only when depth1..64,count0..256. This is the child source buffer, not the already blended destination. Sourceprefix/track identity repeated for independent matching.

Latest sample observation link is stored by track, not asserted as a paired invocation: no thread identity, nesting proof or uninterrupted source lifetime. Offline analysis must check timestamps/source identity and reject stale/mismatched links. Firstthree observations per track/blob/stage,96event/10secondlimit; beep after saved completion retained. Source prefix matcher accepts new event schema. Larger files remain prefix candidates; short known lean fileblocks compare at their exact serialized lengths.

Three actual Lua5.3 mock cases pass: bounded samples and rawhitcounts,latest observation reference,two52byterows,completion beep; badsignature;partialinstallcleanup. These are synthetic mocks, not runtime buffer parity. New script unloads both itself and olderlocomotionlogger; existing emptybreakpointguard remains. No viewer changes.

Run newlogger, move Elsa,pressF8,keepmoving untilbeep,send ce_reftime_*.jsonl. Goal: compare identified file sampling at captured local time against actual child buffer values before changing composition or fingers.
