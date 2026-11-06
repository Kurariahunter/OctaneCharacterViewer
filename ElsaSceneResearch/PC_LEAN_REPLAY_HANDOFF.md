# PC lean IK capture: first offline replay

Capture: octane_20261017_151848_1792264728047355700.json, 60 samples.

The verified PC 8-input/3-output family was captured successfully: ten candidates, including the previously traced thigh-connected pair 0x1e07e324 and 0x1e07e434 in network 0xcbe6c80. Their outputs change across samples. The graph roots remain the updating hair/left-dress/right-dress chains 0x1e07fd08, 0x1e07fdd0, 0x1e07fe74. Other candidates include inactive/template instances and a separate network; candidate identity alone is not actor proof.

Offline replay runs original execute 0x5382f0 from the hash-pinned installed executable in Unicorn, using captured numeric input slots and preserving optional null input 5. A synthetic network with equal frame stamps prevents recursive producer evaluation: this validates the solver against cached captured values, not a full upstream graph execution.

Results for the previously connected thigh pair:
- 0x1e07e324: all three outputs bit-exact numerically in all 60 samples.
- 0x1e07e434: all three outputs exact in 56/60 samples. Maximum sign-equivalent quaternion component errors 0.0025018901 and 0.0250314325; scalar output error 0.0001951456. Non-atomic capture is a plausible explanation for the four mismatches, not established as the sole cause.

Additional changing network: one solver exact 60/60, another 59/60. Inactive/template solvers do not replay their stored outputs from their zero targets; do not treat their stale cached outputs as executed ground truth.

Files: validate_pc_lean_replay.py and pc-lean-replay-validation.json. Original capture unchanged. No game process access or writes are performed by the offline replay.

Next: verify the factory/source mapping of the 8 runtime input slots and 3 outputs against the installed PC OCT (source processors 405/411); port this solver into the PC graph evaluation, then compare generated thigh transforms and dress anchors. Preserve old 13/4 source-family work separately. This is not yet a complete animation converter or proof of clip identity. No additional capture is requested yet.
