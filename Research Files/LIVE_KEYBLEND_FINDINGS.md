# Live KeyBlend selection findings — 2026-10-19 23:53

Capture ce_keyblend_20261019_235313_87652546.jsonl completed at ten-second limit:12before/12after observations,2416rawhits at eachsite. Sixpairquota perparent limits acceptedcoverage. All12pairs pass parent/vtable/stack+16/sequence/keys/count checks and original59DC50 native replay EXACTLY; no rejected/orphan records.

Parent09437D00 has two children and keys[.25,.5], matching authored Speed-key array. Effectiveparameter0.9093604088 in allsix samples selects child1 alone (left/right1,alpha0). Selectedchildpointer09437DC0 equals the secondcapturedKeyBlend node, establishing the runtime parent-child link in this capture. Do not infer physical speedunits or unique actoridentity.

Parent09437DC0 has ninechildren and keys[0,.12,.25,.38,.5,.63,.75,.88,1] (float32), matching authored Directionkeys. Effectivevalues1,0,0,.875,.875,.8884853125. Nativeobserved selections:1 -> indices7/8 alpha1;0 ->0/0 alpha0;.875 ->6/7 alpha.9615384936;.8884853125 ->7/8 alpha.07071097195. This validates nontrivial interpolation and endpointbehavior; exactupperkey canretainpreviousinterval withalpha1 ratherthanselectingonlylastindex. Selecteddirectionchildren have GroupTrack RTTIcandidates.

Expressionpointers onbothparents report FloatParameter RTTI. Replay uses captured effectiveparameter afterexpression/debugoverride, not replayofFloatParameter evaluation itself. Sixsamplesdo not establish full gameplayselectionhistory. Childpointer/keyarray agreement supports Speed/Direction roles but node names/actor identity were not read.

Reports ControllerState/live-keyblend-analysis.json. Combined bounded milestones:1598 exactfile-to-childbufferchannel comparisons;48byte-exactchildblendpairs;12exactparentselectorpairs. Separate captures, not full uninterruptedactorpipeline proof. Nexttrace5A1630 parenttime remapping and two-child parentblend, then join finalcontrolleroutput to rig. No viewer pose/composition changes.
