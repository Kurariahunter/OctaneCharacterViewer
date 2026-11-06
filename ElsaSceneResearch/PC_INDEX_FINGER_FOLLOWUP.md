# Bilateral index-finger follow-up

User confirms both index fingers have unnatural form; other fingers and corrected braid look better. Do not change working middle/thumb/hair paths to compensate.

Checks: left index skin nodes 178/206; right 203/209. Bases follow matching hand outputs 174/199; distal joints use matching index-base converters. Source associations point to the matching Index1/Index2 influence names. Relationship inputs are Index1, Index1Spread, Index2, Middle1, Middle1Spread, Middle2 in authored order. No mapping swap found in this audit.

Local relationship matrices agree with original native Transform point conversion within 3.66e-7 for the audited base indices and 3.78e-8 for distal indices. This checks the coordinate conversion, not anatomical pose correctness or gameplay layer composition. Source run uses -46.9 for both index curl controls and zero spread. Do not negate or reduce these values without distinguishing a source-pose issue from transform/skinning error.

Need a clear close-up showing the offending index shape from the palm and side to identify whether the base bends away, the distal segment doubles back, or the mesh twists/collapses. Existing rendered hand side view partly obscures that distinction. Root cause remains unresolved; no index-specific pose adjustment shipped in this checkpoint.
