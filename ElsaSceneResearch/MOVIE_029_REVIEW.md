# Movie 029 fingertip checkpoint

Reviewed Movie_029.webm (13.533 s) using six one-second samples from the first six seconds, including side and oblique hand views. Visible diagnostic settings: source tip 100 percent, proximal bend approximately -9 degrees, gap closure 100 percent. User accepts first/second knuckle positioning as close but reports distal angle wrong. Do not treat this as proof of original animation parity.

Shared preview now exposes independent distal bone-local offsets: Tip bend X, Tip side angle Y, Tip twist Z, each +/-90 degrees. Y/Z are mirrored between hands; X is shared. Offsets are applied after the existing base/gap and tip-weight diagnostics. Distal joint position and proximal orientation are unchanged by tip-only offsets. There is no third index bone in this exported palette: these rotate Index2_Left/Right, not an invented fingertip joint.

Your knuckles restores the observed -9-degree proximal, gap 100 percent, source tip 100 percent and zero tip offsets. Corrected-hands preview defaults to this observed user diagnostic pose. EditorPrefs stores adjusted diagnostic values between Play sessions for that preview only. Restore fingers still returns all diagnostics to decoded source defaults and saves that selection. Source animation, meshes and importer remain untouched. These visual calibration controls do not resolve the native source-layer composition question.

Next visual step: keep accepted knuckles fixed; adjust Tip bend first, then side/twist only if needed. Record the resulting values before considering a separately named correction preset or baked comparison.
