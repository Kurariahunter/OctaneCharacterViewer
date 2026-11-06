# Blended buffer output bridge capture — 2026-10-20

RTTI BlendedClipProcessor@Samurai resolves vtable1B35CF4,execute531DC0. It evaluates its root track through the embedded object atprocessor+3C,usingbuffer managerprocessor+74,then calls52B3C0 at531E48. Bridge outputarrayprocessor+30,count+34; rows from currentmanagerframe.59D3B0 requiresdepth0;59D720 returnsmanager.table+depth*16. This is the directbuffer-to-output-node stage. Nearby5A0A20 is matrixwork and was excluded fromthistrace.

52B3C0 applies typed predicates,mask-selected scalar/translation/scale/rotation fields andmetadata stamp updates. Onebranch copiesquaternion directly;another normalizeswithsqrt/divide beforewrite. Exacttargettypepredicate comesfromruntime descriptorword/node+10 andglobalmask/valuepairs; do notinfer solelyfromtype names. native_pc_output_bridge.py executes the fullbridge withcapturedtypewords/globals andknown4/32/64bytepayloads,isolatedmemory,managerdepth0;globalsrestoredafterfixture.

Sixsyntheticnativecases pass:scalar,directrotor,normalizedrotor plusmask-zero preservation. Node-stamp behavior checked. These use synthetic typed descriptors, not proof which live types selecteachbranch.

DI3_OutputBridgeLogger.lua uses two read-only hardwarebreakpoints52B3C0entry and531E4Dcallerpostreturn. ExactBlendedClipProcessorRTTI andcallerreturnguards. BeforeECXprocessor,afterESIprocessor;stack+4pairing. Captures current52byte rows,outputarray,indexed typed nodepayloads before/after,nodevtable/descriptorword/stamps and12nativepredicateglobals. Float4,Dilation32,Transform64 only;otherpayloadsomittedwithboundary. Up to256rows/outputs,firstsixpairs perprocessor,96records/10seconds. No gamewrites,injectionorforcedevaluation. ThreeLua5.3mockcases pass:typedwidths/pair/rowextent/beep,signaturefailure,secondbreakpointfailurecleanup.

analyze_output_bridge_capture.py replayscapturedsupportednodes andreportsbyte/stampcomparison andskippedtypes. Requirescompletepredicateglobals,depth0,equalrow/outputcounts,stableoutputidentities/types. No livebridgecaptureyet; no downstreamrigconsumptionoractoridentityclaim. Viewerunchanged.

Run DI3_OutputBridgeLogger.lua,moveElsa,pressF8,keepmovinguntilbeep,send ce_outputbridge_*.jsonl. Knownbipedfilemapcontains49Dilation,45Float,17Transform,1EventSet;EventSetremainsoutside typedpayloadprobe.
