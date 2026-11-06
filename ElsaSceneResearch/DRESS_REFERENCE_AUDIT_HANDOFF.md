# Dress reference-chain audit

Date: 2026-10-16. Follows Movie_013 and SKIRT_BULGE_KNEE_HANDOFF.md.

The active skirt bulge remains unresolved. No preview, source mesh, weights, production importer or animation asset was changed in this audit.

## Findings

Actual evaluator calls from UpperDress_Left/Right (650/655), lower anchors (660/668) and containers (738/753) reach 257 distinct DataNodes in each first-frame clip fixture. The mapping exposes 14 unselected bindings. Active has 13 constant records among these, passive has eight; every present record matches the stored neutral value. Neither clip has a timed command on these omitted bindings. This rules out another non-neutral omitted clip control on the traced dependency set, within our existing structural port mapping. It does not establish the completeness of the engine graph, layers or mapping.

Upper dress chains:
- Left: 649 -> 651 (combined with inverse reference 15) -> 650 (combined with anchor 13).
- Right: 654 -> 656 (combined with inverse reference 14) -> 655 (combined with anchor 13).
- Reference 15 inverts 620; reference14 inverts627. Each of620/627 combines normal input420 with inverse input615/622.

## Executable-backed reference operators

Traced original registration -> allocation -> constructor -> vtable execute:

| Operator | Factory | Wrapper | Allocation | Constructor | Vtable | Execute |
|---|---|---|---|---|---|---|
| InvertDilation | 0x4f09c0 | 0x4e9cc0 | 0x4ddba0 | 0x4c9b80 | 0x1b2eb94 | 0x4d19c0 |
| ConcatenateChainDilation | 0x4f0f80 | 0x4ea1c0 | 0x4ddf60 | 0x4c9ea0 | 0x1b2edac | 0x4d1cb0 |
| ConcatenateChainInverseDilation | 0x4f1ae0 | 0x4eaa80 | 0x4de5f0 | 0x4ca920 | 0x1b2f164 | 0x4d2b00 |

Native one-normal/one-inverse chain fixture must set processor+0x1c to1. Omitting that split count produces an invalid fixture; an initial mismatch was traced to this test setup, not the production evaluator.

100 randomized mixed-axis positive uniform-scale cases per operator pass. Matrix formulas corroborated: inverse(A), B@A, inverse(B)@A, respectively. Maximum errors: 4.5211e-7, 4.9503e-7, 6.2060e-7.

All313 frames (127active,186passive), six reference nodes each (620,627,15,14,651,656): 1878 comparisons pass against original executable routines. Maximum matrix error3.56036e-7. These operators do not explain the remaining bulge within the tested inputs. Their inputs still originate from the bounded evaluator; this is not independent full-engine pose validation.

## Reproduction

Run audit_dress_references.py, inspect_dress_omitted_controls.py, validate_dress_reference_native.py with the existing research Python/dependencies. Output reports: dress-reference-dependency-audit.json and dress-reference-native-validation.json. trace_dress_*.py preserve executable tracing helpers. Native test only executes mapped routine fixtures via Unicorn, not the game process.

## Next boundary

Compare animation layers and original graph update order, especially authored/reference thigh proxy inputs, against a trustworthy original-game pose. Existing local operator tests do not validate full graph scheduling, base-layer blending or visual correctness of the source pose. Do not apply guessed inverse-bind changes or skin-weight edits on the strength of the bulge alone.
