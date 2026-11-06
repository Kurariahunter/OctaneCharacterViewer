# DI3ListOfAllFiles: saved research lead

Reviewed 2026-10-15.

Repository: https://github.com/themadgoblin/DI3ListOfAllFiles

## What was inspected

Read the public repository README, recursive file listing, helperTools/readme.txt, helperTools/generateScript.sh, and sampled/searched Indices/IbufIndex.txt. No repository scripts were executed. The large platform inventories were not downloaded or compared against our local inventories.

## Relevant contents

Platform inventories: Android1.1, Android1.2, NonGOLD-PC, PCGold, PS3-BLES02147, PS3-BLES02148, PS4, PS4Patch, WiiU, WindowsStore, XBOX360.

The README describes IbufIndex as filename occurrence counts across the inventory text files. A count of1 is a candidate for a version-specific filename, not proof of exclusive usable content. Confirm the originating inventory and archive.

Observed examples include psx_emmitt_0.ibuf, psx_crossover_emmitt_0.ibuf, psx_crossover_grimm_0.ibuf, psx_crossover_lola_0.ibuf and related projectile/combat names. These do not independently establish character identities, complete models, playable content or animation availability.

The helper shell script emits one QuickBMS listing command per recursively found file, using disney_infinity_psx.bms. Its documentation says this avoids crashes when processing multiple files together. It is inventory assistance, not an animation decoder. Do not execute its generated commands without checking local paths and arguments.

## Planned use

1. Compare relevant PS4/base-patch, PS3 and PC filename sets against our saved inventories.
2. Search target character codenames and motion-related paths; identify containing archives before extraction.
3. Treat basename-only matches and occurrence counts as leads; verify full archive path, platform/build and actual member bytes.
4. Keep this work separate from executable RelationshipProcessor decoding. It may locate useful samples but supplies no verified processor math.

## Source links

- README: https://github.com/themadgoblin/DI3ListOfAllFiles/blob/main/README.md
- Mesh index: https://github.com/themadgoblin/DI3ListOfAllFiles/blob/main/Indices/IbufIndex.txt
- Helper: https://github.com/themadgoblin/DI3ListOfAllFiles/blob/main/helperTools/generateScript.sh
- Helper notes: https://github.com/themadgoblin/DI3ListOfAllFiles/blob/main/helperTools/readme.txt

This is a saved assessment, not a complete offline mirror. Repository contents can change; record a commit before performing a reproducible cross-version comparison.
