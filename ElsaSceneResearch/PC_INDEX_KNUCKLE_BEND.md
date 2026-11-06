# Index knuckle axis correction

Supersedes PC_INDEX_BASE_DIAGNOSTIC.md: user clarified that the defect is the up/down bend, not lateral spread. The prior rest/source interpolation did not isolate that axis and has been removed. New control: Index knuckle bend (up/down), -90 through +90 degrees, default zero. It postmultiplies the decoded proximal orientation by a bone-local X rotation. Bone-local Z follows the finger segment, so X is the candidate curl hinge (also dominant in the source distal curl quaternion). Anatomical direction still needs user visual verification.

Distal position and rotation are carried rigidly by the proximal rotation delta, preserving the segment length. Tip control remains separate; keep it at 100 percent while testing the knuckle. Restore fingers resets bend offset to zero and tip to 100 percent. This is a reversible Play-mode diagnostic; it does not save a correction to the animation/importer.
