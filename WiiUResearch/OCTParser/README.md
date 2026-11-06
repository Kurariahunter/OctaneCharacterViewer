# Wii U OCT / BinaryTup reader findings

Date: 2026-10-23. Static inspection of the previously decompressed, symbol-bearing
Disney Infinity 3.0 `game.consumer.rpx` in `../RPX`. No running emulator required.
Disassemblies and symbol addresses here refer only to that RPX build.

## Confirmed engine routines

| Routine | Wii U virtual address | Finding |
|---|---|---|
| BinaryTupBlock::Interpret | 0x0431A81C | Verify magic, optionally swap header, verify lengths, initialize strings, optionally swap atoms |
| VerifyMagicNumber | 0x0431A114 | Accepts 0x45017629 and opposite-endian 0x29760145 |
| VerifyHeader | 0x0431A1E8 | 60 + string bytes + atom bytes must equal supplied file length; checks version |
| InitializeStringArray | 0x0431A298 | Strings start at byte 60; scan the declared byte region, including empty string at index zero |
| GetAtomData | 0x0430D3A0 | Atom start = 60 + header uint32 at +0x0C |
| GetAtomCount | 0x0431AAA4 | Header uint32 at +0x14 |
| ReadPackedUint | 0x0430D418 | Variable-width unsigned fields |
| ReadPackedInt | 0x0430DCD4 | Sign-extends packed integer values |
| GetAtomSize | 0x0430DF4C | Computes size from flags, optional name, count, and element width |
| BuildAtomHierarchy | 0x020F9D40 | Extracts depth from high six flag bits; begins with the first root record |
| GeometryNode::SerializePrim | 0x020B1324 | Located/disassembled; renderer interpretation is follow-up work |
| GeometryNode::Serialize | 0x020B1A98 | Located/disassembled; renderer interpretation is follow-up work |

The executable supports either byte order by converting to native order. Our
Python reader instead reads fields directly in the byte order selected by magic.

## Header and atoms

- +0x00: magic; +0x04: float version (both samples approximately 1.1).
- +0x0C: string table byte length; +0x10: atom byte length; +0x14: atom count.
- Header length is 0x3C. Other header fields remain uninterpreted here.
- Strings are null-terminated inside the declared string table region.
- String indexes use 2 bytes with at most 65,536 strings, otherwise 4 bytes.
- Each atom begins with uint16 flags and its string-table key index.
- `flags >> 10`: depth. `flags & 3`: aggregate=1, list=2, scalar=3.
- `flags & 4`: optional name index follows the key.
- `(flags >> 3) & 7`: string=1, float=2, integer=3, binary=4.
- `((flags >> 6) & 3) + 1`: packed count width.
- `((flags >> 8) & 3) + 1`: packed integer width.
- Floats occupy 4 bytes. Binary scalar count is its byte length.
- An initial depth-zero root is valid. It is not an extra corrupt record.

## Why the PC-assuming reader failed

The installed AssetWiiUdio DI3MeshReader starts at byte 61, looks for a sentinel,
consumes another uint16, reads little-endian fields, and rejects depth zero.
For Grimm it consequently starts its hierarchy at 3326. The engine-declared
start is **3321**, whose first bytes are `00 01 00 00`: aggregate root, depth 0,
empty key. The next record begins at 3325. This is a header/record parsing issue,
not evidence of damaged archive extraction. Merely removing the depth guard
would leave other assumptions wrong.

## Reproduced sample results

`read_binary_tup.py` generates flat JSON records with explicit parent indexes,
offsets, values, names, and byte-exact base64 binary fields.

| Sample | Strings | Records | Exact EOF / header count |
|---|---:|---:|---|
| psx_grimm_pieces.oct | 230 | 1118 | Pass |
| psx_loc2_freighterconsole_debris.oct | 240 | 790 | Pass |

Every record is bounds checked, string indexes are checked, parent/depth
relationships are checked, and file and atom counts must match their headers.
These are structural validations, not rendered-geometry validation. The reader
has not yet been tested on a large corpus, PC files, or every supported atom type.

Grimm's parsed tree identifies `psx_grimm_pieces.mtb`,
`psx_grimm_pieces_0.vbuf`, `psx_grimm_pieces_0.ibuf`, and the
`characters__psx_grimm__materials__psx_grimm` and `...psx_grimm_cap`
materials. It also exposes buffer offsets, base vertex indexes, index-stream
references, vertex-stream references, and vertex format CRC values.

## Next implementation step

Adapt the C# structural reader to these header-based rules while keeping the
existing PC path covered by regression samples. Then validate Wii U vertex
layouts, index byte order, stream lengths, triangle ranges, and rendered geometry
against GeometryNode / OctFileInterpreter routines. Do not assume that decoding
the OCT tree alone makes the PC mesh extraction loop compatible with Wii U.

Source archive and game assets remain unchanged. Research scripts/notes and
parsed sample results are mirrored into the Unity project's WiiUReference folder.
