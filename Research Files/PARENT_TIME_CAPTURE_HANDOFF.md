# Parent-to-child time capture — 2026-10-19

Original5A1630 arithmetic/control flow validated offline in native_pc_keyblend_time.py. For tested positive parentduration, normalizedtime=f32(incomingtime/parentduration), childtime=f32(childduration*normalizedtime). Low-duration branch returns normalized1 in the zero-durationfixture. Single-child and two-child branches calldifferent verifiedsites.61nativecases pass; bufferpush,virtualchildexecution andblendcalls are intercepted boundaries, not fullparentoutput validation.

New DI3_ParentTimeLogger.lua uses fourhardwareexecutionbreakpoints:5A1630parententry,5A1695singlechildcall,5A16CDleftchildcall,5A1722rightchildcall. EntryECXparent,ESPreturnbase; incomingtimeESP+4, durationparent+14,alphaparent+48,selectedindices+4C/+50,childpointer/durationarray captured. ChildcallEBXparent,ECXchild,ESPargumenttime; singlebranchstack+20 andtwochildstack+32 link back toparententrystack. Parentnormalizedtime remains atoriginalstack+4 after5A1667 store and isrecorded atchildcalls.

ExactKeyBlendRTTIguard,1..64children,firstsixentriesperparent,96records/10seconds,PE32/signatures,oldloggercleanup,completionbeep. Nestedparents getdifferentcontextkeys; entriesabovequota clearcontext ratherthanreusingstaleentry. No parentexit/threadidentity proof; stack/pointer/durationchecks required offline. No gamewrites,injectionorforcedevaluation. Allfourhardwaredebugslotsused.

ThreeLua5.3mockcases pass:allthreebranchargumentrouting/stackcontext,payloadwidth,lifecycle/beep;signaturefailure;secondbreakpointfailurecleanup. Mockbranchrouting is not a claim that allthreebranches occur inoneevaluation. analyze_parent_time_capture.py compares native arithmetic againstcapturedcalls;no livecaptureyet. Viewerunchanged.

Run DI3_ParentTimeLogger.lua,moveElsa,pressF8,keepmoving/changingdirectionuntilbeep,send ce_parenttime_*.jsonl. This checks phase/time mapping; fulltwochildparentbufferblend remainsnextstage.
