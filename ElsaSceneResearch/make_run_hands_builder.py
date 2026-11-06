from pathlib import Path
import shutil
root=Path(r'C:\Users\Kurar\Disney Reloaded\Assets')
src=(root/'DI3PCRunLeanPreview/Editor/DI3PCRunLeanPreview.cs').read_text()
src=src.replace('DI3PCRunLeanPreview','DI3PCRunHandsPreview').replace('PC_RunLean','PC_RunHands').replace('Run Lean','Run Hands').replace('pc-run-lean-animation','pc-run-hands-animation')
src=src.replace('Assets/DI3PCRunPreview/Generated/grl_bm_runf_PC_Run.prefab','Assets/DI3PCRunLeanPreview/Generated/grl_bm_runf_PC_RunLean.prefab')
p=root/'DI3PCRunHandsPreview/Editor';p.mkdir(parents=True,exist_ok=True)
(p/'DI3PCRunHandsPreview.cs').write_text(src)
validation=Path(r'C:\Users\Kurar\.codex\visualizations\2026\09\19\01a0b763-cacf-7eb0-a8d4-4f4c2ba597f1\DI3ConverterValidation\Assets\DI3PCRunHandsPreview\Editor');validation.mkdir(parents=True,exist_ok=True)
shutil.copy2(p/'DI3PCRunHandsPreview.cs',validation/'DI3PCRunHandsPreview.cs')
