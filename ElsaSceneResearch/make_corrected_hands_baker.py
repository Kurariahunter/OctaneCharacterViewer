from pathlib import Path
p=Path(__file__).parent
s=(p/'bake_pc_run_hands.py').read_text()
s=s.replace('names=names+', '''parents['hair01']='hairStart'
parents['hair02']='hair01'
bindlocals={name:np.linalg.inv(worlds[parent])@worlds[name]if parent else worlds[name]for name,parent in parents.items()}
names=names+''')
s=s.replace('pc-run-hands-animation.json','pc-run-hands-corrected-animation.json').replace('pc-run-hands-validation.json','pc-run-hands-corrected-validation.json').replace('_PC_RunHands','_PC_RunHandsCorrected')
(p/'bake_pc_run_hands_corrected.py').write_text(s)
