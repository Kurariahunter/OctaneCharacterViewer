# AssetWiiUdio Wii U OCT integration — 2026-10-23

Installed `DI3MeshReader.cs` in `C:/Users/Kurar/Documents/AssetWiiUdio`.
Original preserved as `DI3MeshReader.before-wiiu.cs` in this research folder.

Implemented:
- Magic-selected big/little endian reads.
- Header-declared string/atom boundaries and atom-count validation.
- Packed count, signed integer, optional atom-name and depth-zero root handling.
- Explicit VertexStreamReferences / IndexStreamReference resolution.
- Observed static layout: 16-byte stride, position Type 2 at offset 0,
  texcoord0 Type 45 at offset 12, no extra stride, TRIANGLES only.
- Correct byte order for vertex floats, UV halves, and index values.
- Existing vertex/index buffer bounds and triangle-index checks retained.
- Other layouts fail explicitly rather than guessing.

Actual C# mesh results:

| Wii U sample | Vertices | Triangles | Primitive groups |
|---|---:|---:|---:|
| psx_grimm_pieces | 5298 | 7909 | 7 |
| psx_loc2_freighterconsole_debris | 1068 | 741 | 2 |

Both extracted to OBJ with finite coordinates/UVs and valid indices.
`Parsed/geometry-check.png` is an inspected solid-shaded projection of those
actual exported triangles. Grimm has recognizable clothing/body pieces. This
does not verify scene assembly, bind transforms, skinning, textures, or every LOD.
Freighter includes overlapping geometry pieces in local coordinates.

PC regression: installed-game Elsa OCT parsed in C#; independent Python reader
verified 12,950 atoms, 1,983 strings and exact EOF. PC full mesh regression was
not completed because the descriptor folder lacks its companion buffers.

Full WPF application compiled Release with 0 errors and 17 warnings (nullable
annotations and current GX2 stackalloc analyzer warnings). No interactive WPF
preview session was exercised. Build output: `Build/AssetWiiUdio.exe`.
The GX2 source currently on disk differs from the earlier external-adapter
revision; it was not overwritten during this OCT task.

Tests: `MeshCheck/MeshCheck.csproj` links the actual staged reader; output OBJ
files are in `Parsed`. Original game assets and archives were not changed.
