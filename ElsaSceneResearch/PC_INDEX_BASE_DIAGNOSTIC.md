# Index base-joint isolation

Screenshot 113041 supports investigating the proximal (hand-to-index) joint rather than only the tip. Shared preview adds Index base test (rest to source), initially 100 percent. It interpolates the base orientation between the original PC inverse-bind-derived rest orientation relative to Hand and the current decoded source pose. The distal joint position and orientation are carried rigidly with that base change, preserving segment spacing; the existing tip control applies afterwards. Both hands are affected only on the updated example. Restore fingers resets both sliders. This is a diagnostic, not an established decoder correction.

Suggested comparison: restore fingers first (tip 100, base 100), then vary base only. A smaller percentage is not automatically a verified game value. Working fingers, hair, source clips and mesh weights are unchanged. Exact native relationship-to-gameplay pose composition remains under investigation.
