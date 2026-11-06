"""Failure boundaries for the bounded anchor adapter."""
from evaluate_pc_dress_anchors import AnchorGraph
seed=[0,0,0,1,0,0,0,1]
g=AnchorGraph({'unsupported':{'operation':'Unknown','inputs':[{'node':'seed'}]}},{'seed':seed})
try:g.run('unsupported')
except ValueError as e:assert 'Unsupported descendant' in str(e)
else:raise AssertionError('Unknown descendant accepted')
g=AnchorGraph({'multi':{'operation':'VariantAdapter_4dc8c0','inputs':[{'node':'seed'},{'node':'other'}]}},{'seed':seed})
try:g.run('multi')
except ValueError as e:assert 'Unsupported variant' in str(e)
else:raise AssertionError('Unvalidated multi-input variant accepted')
print('Unsupported operators and multi-input variants correctly rejected.')
