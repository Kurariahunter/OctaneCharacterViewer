# Matching PC Unity package checked

2026-10-17. User archive C:/Users/Kurar/Disney Reloaded/Assets/DI3Converted/fro_elsa_3.0_PC.7z inspected and extracted separately to PCImportPackageCheck. Original project/package unchanged.

Archive contains converted prefab, mesh asset, OBJ, materials, textures, meta files,ImportReport and animation inventory. It does not contain raw source OCT/BENT files. The ImportReport identifies an existing Library/DI3ZipCache/a83da00a4dcb40c2bf80eaa8bfda96ae source cache. Read-only hashes of that cache's model,BENT,active idle and passive idle exactly match our independent installed-game extraction. Thus report/cache provenance corroborates that this conversion uses the matching PC assets. It is not an embedded raw-source hash verification of the7z.

ImportReport lists5419vertices,8935triangles,62bones. It explicitly reports nearest-weighted-ancestor/helper-parent approximations, no original animations or procedural constraints, recalculated normals, feet placed at origin,scale1. Eye import was skipped for an unsupported final eyelid connection. These limitations must be retained when using the prefab as a baseline; they are not evidence of animation decoding failure in the source data.

Use this package as the matching PC visual/mesh/material reference while implementing IkLean2LinkProcessor and matching PC clip/control mappings. Preserve old research previews as a separate asset-family experiment. No prefab was replaced or imported from this archive into live Assets in this check; extraction stayed under the research directory to avoid GUID collisions.

Verification: pc-import-package-verification.json;verify_pc_import_package.py. Four raw cache/installed pairs match exactly. Current installed model SHA38ba59d139a5a481604ff2668d5a8c60b237da51bb4e6af2c65b866e0275141d.
