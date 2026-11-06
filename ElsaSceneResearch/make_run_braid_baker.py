from pathlib import Path
p=Path(__file__).parent
s=(p/'bake_pc_run_hands_corrected.py').read_text().replace('from evaluate_pc_feedback_dress import FeedbackDressEval','from evaluate_pc_braid import BraidEval').replace('class RunEval(FeedbackDressEval):','class RunEval(BraidEval):')
s=s.replace('+["hairStart"]','+["hairStart","hair01","hair02"]')
s=s.replace('e.raw.run(skin["dressRightStart"])','e.raw.run(skin["dressRightStart"]);e.raw.run(skin["hair01"]);e.run(skin["hair02"])')
s=s.replace('pc-run-hands-corrected-animation.json','pc-run-braid-animation.json').replace('pc-run-hands-corrected-validation.json','pc-run-braid-validation.json').replace('_PC_RunHandsCorrected','_PC_RunBraid')
s=s.replace('braid dynamic segments remain fallback.','braid source DynamicChain548 with native chronological stepping and local Aim feedback evaluated; game parity not established.')
(p/'bake_pc_run_braid.py').write_text(s)
