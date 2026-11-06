# Live blend contributor checkpoint

2026-10-16. Capture octane_20261016_234212_1792208532622535200.json.

Both candidate upper-dress controls contain exactly one unchanged contributor across60samples: controller0xc39a200, priority/group float5,flag39=0, scalar factors atcontroller+2c/+30both1. Left uses inputslot110/weightindex860; right111/861. Node container0xccacb00 declares112slots. This identifies concrete contributors but not their active clip names. A controller can play/change clips without changing pointer; stable controller addresses do not establish a static animation state. Effective table weights were not captured yet.

Container vtable methods relocate to count getter0x7b2500 (returns[ecx+20]) and slot getter0x4b4f00 (returns pointer array[ecx+1c][index]). These unmodified accessors were disassembled; no in-process calls used. Updated reader resolves a contribution slot only if both methods match expected code addresses, count<=4096 and index<count. It records the resolved input node/header/payload and table weight from the separately traced controller+28 -> object+10 array. Unknown accessor methods or unreadable memory stop that contribution read rather than invent data.

Synthetic tests pass for proper slot resolution, bounds rejection and unknown accessor rejection, alongside previous output-alias/table-size/tag tests. New field reads still require a live capture. The previous capture does not contain the pointed-to input array bytes, so they cannot be recovered offline from it.

Next: same administrator launcher,game foreground. New capture includes resolved inputs and raw table weights, enabling source-control comparison at the contributor level. No claim of named active clip logger or full blend emulation. No game memory writes, mesh edits or Unity preview changes.

Reports/scripts: OctaneLiveInspector/blend-contributor-analysis.json,analyze_blend_contributors.py,upstream_graph.py,test_upstream_graph.py.
