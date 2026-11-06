# Parent left/right blend capture — 2026-10-20

New DI3_ParentBlendLogger.lua captures four verified sites: left before5A16EE/after5A16F3, right before5A1740/after5A1745. EBXparent,ESIselectedchild;ECXmanager before,EDImanager after;ESP+12cleanup. ExactKeyBlendRTTI guard,selectedchild pointer checked against parent childarray/index. Pair key includes parent/side/manager/child/stack. Captures source and destination before, destination after, parentheader84,childheader32,parentalpha,indices and dispatchedweight/mode/filter.

Only nullfilter/modes0or1,depth1..64,rowcounts<=256;firstsixpairs per parent/side/child/mode,96events/10seconds. Allfour hardwarebreakpoints used; old parenttime/keyblend/postblend probes unload. Existing PE32/signaturechecks,cleanup andsavedcompletionbeep retained. No injection,gamewrites orforcedevaluation. Samplingquota can end between sides; do not assume fullparent invocation from adjacent records alone.

Raw native replay analyzer nowaccepts both child andparent schemas. Parentvalidation checks side/parent,selectedpointer,weight1 onleft/parentalpha onright,mode derivedfromchild+8,stack/depth/destinationidentity. Sixnative-generated analyzercases pass: childexact,stackreject,destinationreject,outputalterationdetect,parentexact,parentwrongside reject. ThreeactualLua5.3mockcases pass: bothsidepairs/selectedpointer/bufferwidth/beep,signaturefailure,secondbreakpointfailurecleanup. No liveparentblendresult yet.

Run DI3_ParentBlendLogger.lua,moveElsa,pressF8,changedirectionuntilbeep,send ce_parentblend_*.jsonl. Analyzer explicitoutputpath should preserve earlierchildblendreport. Viewer unchanged; nextjoinleft-after/right-before buffers onlywithmatchingparent/context/destination andqualifiedscheduling scope.
