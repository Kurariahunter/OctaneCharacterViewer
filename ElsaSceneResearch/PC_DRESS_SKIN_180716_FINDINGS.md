# Live downstream capture 18:07:16: world consumer boundary

Capture: OctaneLiveInspector/Captures/octane_20261017_180716_1792274836164213400.json.

The discovery scan completed, reading632190245bytes with0failed chunks. It accepted34recognized processor records. For each of the4dress-shaped chain candidates it found exactly1local compose consuming the cached orientation, but0matching local/anchor world concatenation paths. Thus the saved full-path list is empty and all240dress_skin sample arrays are empty. This capture does not contain local/world numeric payloads for a new transform comparison. The dynamics samples remain available.

Updating previously connected chains remain0x1e07fdd0and0x1e07fe74. All240snapshots per chain are within10global frames, measured gravity is unchanged and capsule count remains0. No dynamics field errors were recorded. Changed read-window stamps29left/27right are still non-atomic capture boundaries.

The failed hypothesis is the runtime discovery requirement that a recognized2-input ConcatenateChainTransform consumes the exact composed local Transform followed by the exact anchor, with the output producer pointing back to it. The capture does not establish which of these assumptions fails. Possible runtime graph/layout differences are hypotheses, not diagnoses. No process is currently running for further read-only inspection.

## Tool repair

The original scan discarded recognized records and rejected candidates, and required a complete path before capturing anything. The updated tool now:

- Retains bounded recognized processor records and up to64rejected examples with known execute, raw header and bounded array references where readable. These diagnostics are evidence, not accepted graph edges.
- Accepts a unique, verified local compose as a local-only path when no full path matches. It continues to reject ambiguous consumers and revalidates links each sample.
- Captures local numeric Transform/components, quaternion, anchor and particle positions even if world remains unresolved. It does not fabricate a world node.
- Reports local-path and full-path counts separately in the summary. Existing verified_paths remains the full-path count.

Updated synthetic tests pass for local-only capture and ambiguity rejection in addition to the earlier stale-link/alias/stamp/payload checks. Existing dynamics tests pass. No Unity/game assets changed.

Run the same Capture Dress Skin Transforms.cmd again with Elsa active. The next fullJSON should supply localTransform numeric comparison data and the missing world-link diagnostics even if no complete path is found. Live numeric transform validation remains pending.
