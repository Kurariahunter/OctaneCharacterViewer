# KeyBlend selector capture — 2026-10-19

RTTI vtable1B38E94+24 resolves execute5A1630. Parentselection helper59DC50 chooses indices at+4C/+50 andalpha+48 using childarray+24/count+28 andexplicitkeys+34/count+38. Parameter comes from expression+40 through59D3C0 or fallbackfloat+44, then optionaldebugoverride.59DDA0 callsselector and interpolates childduration into parent+14.5A1630 remapsincomingtime by parentduration andchildduration, evaluates leftchild andconditionallyright, blendsleftat1 andrightatalpha. Those are staticdisassembly observations, not yet liveselectionparity.

native_pc_keyblend_selector.py executes original59DC50 with captured-effectiveparameter supplied as constant (null expression, debugoverride disabled). Explicitcompletekeys or boundeduniformcase only.229nativecases pass againstfloat32intervalreference: Speedkeys.25/.5,Directionkeys0/.12/.25/.38/.5/.63/.75/.88/1,rangeedges,anduniform2/9childcases. Expression evaluation itself remains outsidefixture.

New DI3_KeyBlendLogger.lua: twohardwarebreakpoints at59DC8B (afterexpression/debugoverride,beforeselection) and59DDA9 (knowncallerafterreturn). BeforeEDXparent/ESPparameter;afterESIparent,ESP+16. Captures effectiveparameter,keys,count,childpointer/header32,expressioncandidate,parentheader84;afterselectedindices/alpha. ExactKeyBlendRTTI guard,callerreturnguard,knownstackpair,firstsixpairs perparent,96events/10seconds,cleanupandcompletionbeep. No gamewrites/injection/forcedevaluation. ThreeLua5.3mockcases pass includingnormalpairedparameter/keywidth,signaturefailure,secondbreakpointfailurecleanup.

analyze_keyblend_capture.py replays captured effectiveparameter withfile-independentnative selector,checks vtable/keys/stack/parentidentity andpriorstate. No livecapture yet. Childheaders are not motionnames; keyarray match can suggest Speed/Direction but doesnot uniquelyidentifyactor. Nextcomparelive selector outputs beforeintegratingparentweights or guessing animationtime.

Run DI3_KeyBlendLogger.lua,moveElsa,pressF8,continuechangingdirectionuntilbeep,send ce_keyblend_*.jsonl. Viewerunchanged.
