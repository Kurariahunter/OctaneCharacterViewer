# Indexed filter application checkpoint — 2026-10-18

Continuation of PC_PARAMETER_BINDING_FILTER_HANDOFF.md. Same SHA-pinned 32-bit PC executable. All VAs use preferred base 0x400000; RVAs and code hashes are recorded in pc-indexed-filter-manifest.json.

## Confirmed consumption path

The complete original native Dilation blend routine at 0x4e35d0 consumes each 8-byte contributor entry:

- First word: contributor/controller pointer.
- Second word bits 0..11: source channel slot in the contributor's source container.
- Second word bits 12..23: index into the referenced Filter float array.
- Upper byte contains additional runtime flags; this checkpoint does not fully define every high bit.

When controller +0x28 contains a Filter pointer, the routine loads its payload at Filter +0x10 and selects coefficient[(packed >>12)&0xFFF]. A null Filter pointer uses coefficient 1. The selected coefficient is multiplied by an optional scalar node at controller +0x2C (also defaults to 1). Node +0x30 is read separately; these tests leave it at 1 and do not generalize its composition/priority semantics.

Source channel lookup independently uses packed&0xFFF. Source and coefficient indices must not be substituted for one another.

## Native test results

validate_pc_indexed_filter_blend.py invokes the complete unmodified original blend function on explicit synthetic source containers and Filter payloads. Two source channels x three coefficient indices x three scalar factors = 18 checks. Noncommuting rotor inputs and distinct translations ensure that selecting the wrong source channel or coefficient is observable. One additional null-Filter case uses a deliberately nonzero filter index and confirms the default coefficient 1.

Fixture scope: one unflagged base and one flagged additive contributor, same priority 5, unit scale, full-replacement processor flag, no default-network state, scalar at +0x30 fixed to 1. Maximum rotor error 5.82e-8, translation error 9.54e-8. These are fixture math errors, not a measurement of source game animation parity.

The replay adapter now accepts explicit source_values/source_index and filter_values/filter_index. Existing default compacted capture behavior remains unchanged. Test allocations bound source arrays to 4 entries and filter arrays to 64 entries to keep fixture regions separate; the native bitfields remain 12 bits. The pre-existing 36 controlled blend checks still pass with unchanged reported errors.

## Existing capture cross-check

A read-only audit of ce_blendexec_20261017_204631_310307171.jsonl found 167 contribution records. All previously logged slot and weight_index values match the native extraction masks; 161 records have different source/filter indices and there are 41 distinct index pairs. 158 contributions have no Filter pointer. This corroborates the bit extraction with previously captured metadata, but the capture still lacks verified actor ownership and complete authored connection tables. Do not assign these records to Elsa merely because the viewer uses Elsa.

Evidence: audit_captured_filter_indices.py and pc-captured-filter-index-audit.json.

## Important distinction: mirror remap is not Filter weights

The optional third argument of clip-buffer dispatcher 0x5a14d0 reaches 0x59f6a0 / 0x5a0490. In those paths, the payload is interpreted as 32-bit remap entries with low30 target index and high2 reflection bits. It is not read as a float coefficient array.

The new static trace distinguishes this mirror/remap table from the Filter object used in 0x4e35d0. The clip-buffer dispatcher still uses a single passed scalar for that operation; do not insert a Filter pointer into its mirror argument. The resolver at 0x774500 also follows separate named Filter and Mirror lookups, storing references at +0x28 and +0x4C respectively.

The mirror path is statically disassembled here, not covered by a new full mirror-evaluation fixture. Its complete mapping and reflection behavior remain separate research.

## Mapping not yet solved

We have verified how the blend consumes packed source/filter indices and the coefficient product in a controlled case. We have not completed how those packed indices are constructed from authored port/connection tables, how every channel type uses weights, or how the active actor chooses masks/layers.

The function at 0x4cec00 was initially saved under a contributor-table-builder candidate filename. Its inspected code is connection setup/mapping and calls registration through 0x50dfe0; it is not yet proven to be the builder of the 8-byte packed contributor table. Keep that distinction in subsequent work.

Next target: trace the relevant connection registration/processor setup into the final packed entry, map its filter index back to the exact authored array order, then test it against a known source graph. Live Speed/Direction updates and external-channel precedence remain other open requirements.

No viewer animation changes and no new capture requested. Source coefficient mappings must be verified before any masks replace the recorded viewer fixtures.

## Reproduce

python validate_pc_indexed_filter_blend.py
python validate_pc_blend_controlled.py
python audit_captured_filter_indices.py

All original function execution is offline through the existing Unicorn harness. No new game-memory hooks or writes.
