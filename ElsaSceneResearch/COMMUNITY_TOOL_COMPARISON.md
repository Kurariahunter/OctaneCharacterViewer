# Community research cache: themadgoblin repositories

Reviewed and cached 2026-10-15. This is a source/documentation comparison, not functional validation. No downloaded code or executables were run. No game assets, saves, NFC tags, production importer or Unity scenes were modified.

## Reproducible cache

Each repository folder contains repository.json (commit, branch, retrieval date and API license metadata), tree.json (complete returned Git tree), manifest.json (cached/skipped paths and hashes), and source/ with original file bytes. All 47 cached files were checked against both their pinned Git blob SHA1 and recorded SHA256. The cache is selective, not a full clone; executables, DLLs, screenshots and unrelated binary dependencies are generally omitted and listed in the manifests. Small mesh test fixtures are included as data.

| Repository | Pinned commit | Cached / listed files |
|---|---|---|
| [DI3ModelConverter](https://github.com/themadgoblin/DI3ModelConverter) | `a956d107e72227e8fde4e5a69c6435634093fa3a` | 11 / 12 |
| [DI3TextureExtractor](https://github.com/themadgoblin/DI3TextureExtractor) | `54400f9d56e2c0b06358e658121eec5d03e23775` | 21 / 115 |
| [DI3SaveGameEditor](https://github.com/themadgoblin/DI3SaveGameEditor) | `fb3ba4425b80c1255a6dabeda51dbcdb58689838` | 10 / 17 |
| [DI3-blenderExporter-ibuf-vbuf](https://github.com/themadgoblin/DI3-blenderExporter-ibuf-vbuf) | `c4a33755c6a2005febe0765884b57fa76229ddf6` | 2 / 2 |
| [DI3TextureNames](https://github.com/themadgoblin/DI3TextureNames) | `4a9730b49fdf206084d743b4248744a4cddd707f` | 3 / 5 |

The complete DI3TextureNames/outputClean.txt dataset is cached: 20,063,501 bytes. It is text, not a texture collection. texture-name-research-matches.txt contains 167 candidate lines mentioning fro_elsa, avg_thor or tcw_yoda. Those matches have not been applied to our materials or validated against the actual archives.

## Comparison with our work

### DI3ModelConverter

README and Python source cover IBUF/VBUF to OBJ and experimental reverse conversion. reader.py is attributed to zzh8829 and reads scene/container records; that is not evidence of fully decoded skeletal animation. This belongs to the same historical tool family referenced earlier in our research, but a byte-for-byte comparison with the johnlogostini fork has not been performed.

Useful: static-buffer examples, half-float handling, tuple/container reader comparison, small cube fixtures. Source uses native struct formats and signed index handling in places, so it is not a universal layout specification. README explicitly says reverse OBJ conversion does not work directly without modifications. Do not infer working rig/animation export.

Our Elsa skinned sample uses24-byte primary vertices plus a separate auxiliary stream; do not replace it with the generic static layout. Compare actual source mesh descriptors, buffer lengths and index ranges before adapting code.

### DI3TextureExtractor

Go source extracts character archives through QuickBMS and derives texture archive names from the first two hex characters of8-byte texture IDs. README notes textures may already be embedded in extracted character folders instead of global texture archives. This supports our existing local/extracted/global fallback strategy; it does not establish every material's correct color/normal assignment.

Source caveats: listTextures.go checks BNDL, assumes a texture-count field at0x1C, takes only its first byte, then reads fixed8-byte IDs with4-byte delimiters. readNextBytes uses File.Read rather than an explicit exact-length read. Treat it as a historical heuristic rather than replacing our bounded/chunk-aware parser. extract.go launches bundled tools and depends on Windows paths; it was only read as text.

### DI3SaveGameEditor

Source covers disk-save compression/decompression and screenshots. inflate.py reads a six-uint32 outer header, scans for CMP1, reads sizes and checksum fields, and uses zlib. Packing computes Bob Jenkins-style hashes for compressed/uncompressed bytes; this is not the same as a CRC32 claim. Decompression prints stored checksum fields but the inspected path does not compare them against computed hashes. Packing hardcodes version519 and writes StorageEncryption=false; reading a flag is not implementing decryption.

README lists PC1.0 and WiiU2.0 as working, PC2.0/3.0 as untested. PC uses little-endian while the CLI defaults to big-endian; future tests must select the platform explicitly. No local save round-trip has been tested.

Useful for later save-file structure, integrity and thumbnail research. These are disk saves, not our320-byte figure BIN dumps: this repository does not by itself identify NFC XP/level fields or solve portal data decoding. Do not apply save offsets/checksums to tags.

### DI3-blenderExporter-ibuf-vbuf

README and script.py describe a Blender mesh exporter with local-space positions, UV seam duplication, triangulation,16-byte position/half-UV vertex records and little-endian uint16 triangle indices. Position uint32 fields carry the float32 bit patterns, not integerized coordinates. README reports Blender4.4 testing and claims DI/Cars3 use; we have not tested those claims locally.

Useful for static-mesh round-trip experiments and explicit buffer layout examples. The inspected script does not produce OCT metadata, material bindings, normals/tangents, skin weights, bone hierarchy or animation. Generating IBUF/VBUF alone does not establish a complete game-ready asset. Its16-byte layout differs from our rigged Elsa24-byte stream. Preserve actual game-specific layout descriptors and prerequisites.

### DI3TextureNames

README describes a Gold-version MTB-path-to-texture-ID index. This is immediately useful as a searchable external hint for missing/shared textures and candidate material archives. Keep full archive/member provenance, not just a basename.

It is generated by a fixed-layout lister, so its entries are candidates, not verified material semantics. Some README example IDs visibly resemble encoded ASCII filename fragments, which reinforces the need to verify BNDL/chunk boundaries and actual DDS payloads. An ID occurrence alone does not prove a color/normal role, character identity or usable texture. No mappings have been imported automatically.

## Suggested order for future work

1. Compare cached Elsa/Thor/Yoda texture-name candidates with current material diagnostics and extracted/global texture inventories. Verify actual texture bytes and full material provenance.
2. Compare the cached mesh readers/exporter with our supported static/skinned layouts using small fixtures; keep custom-model round trips separate from animation decoding.
3. Test save unpack/repack on disposable file copies with explicit endianness and independently validated integrity fields; disk-save results stay separate from figure BIN research.
4. Continue RelationshipProcessor tracing for animations. None of the inspected repositories supplies a demonstrated complete animation/foot-target decoder.

## Attribution and limits

Original files remain under source/ with upstream names/content; local assessment is this file. Preserve upstream copyright and license files where available. Missing or unspecified license metadata is not a grant of a new license. Source inspection is not confirmation of game compatibility. The cache is pinned to the commits above; future updates should be cached separately or compared explicitly rather than silently replacing this evidence.
