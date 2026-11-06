from pathlib import Path
p=Path(__file__).parent
source=(p/'bake_pc_run_lean.py').read_text()
source=source.replace('class RunEval(FeedbackDressEval):', 'from pc_finger_controls import prepare_fingers\nnames=names+[n for n in worlds if any(s in n for s in ("Thumb","Index","Middle"))]+["hairStart"]\nclass RunEval(FeedbackDressEval):')
source=source.replace('apply_lean(e);','apply_lean(e);prepare_fingers(e);')
source=source.replace("name+'_PC_RunLean'","name+'_PC_RunHands'")
source=source.replace('pc-run-lean-animation.json','pc-run-hands-animation.json').replace('pc-run-lean-validation.json','pc-run-hands-validation.json')
source=source.replace('31 source-driven bones; remaining palette bones inherit bind offsets.','Native finger relationships and source hairStart output added; braid dynamic segments remain fallback. Remaining palette bones inherit bind offsets.')
(p/'bake_pc_run_hands.py').write_text(source)
