# Live post-blend replay findings — 2026-10-19 23:46

Capture ce_postblend_20261019_234640_87259843.jsonl contains48before/48afterrecords,96eventlimit.204rawhits at eachsite; threepair-pertrack quota limits acceptedcoverage. All48pairs validate manager,track,stack+12cleanup,depthpop,destinationframe/data/extent. No orphan/rejected pairs.

Original5A14D0 dispatcher replay produces destination buffers BYTE-FOR-BYTE identical for all48pairs,4965rows (258180bytes),maximumfinitecomponenterror0;allmasks exact. Mode1/weight1:26pairs;mode0/weight1:14pairs;mode1/0.899999976:6pairs;mode1/0.850000024:2pairs. This is full raw52byte row replay from captured source and initialdestination, not isolatedlogicalTRSarithmetic.

Source matcher onbeforeevents yields candidates for runlf,runf,runl,runrf,run_upbody_add and corresponding leantracks. Largerblocks remain256byteprefixcandidates;shortleanblocks fullycovered byfilelengthcomparison. Two unknownsources also replay exactly; unknownfileidentity is separate fromnumericoperatorvalidation. Matcher nowaccepts blend_before directly.

Combined evidence: filechannel samples match1598runtimechildbufferchannels in priorcapture; capturednativechildblend results now match48livepairs. These are separatecaptures and boundedsegments, not one uninterrupted end-to-end fullactor reconstruction. ParentKeyBlend direction/speedselection,phase/layer scheduling,non-nullfilters,finalcontrolleroutput andskinpalette remain unverified together. Currentviewerfixturecomposition still not declared fullgameparity. No poseoffsets orviewerchanges.

Next: reconstruct/join parentKeyBlend child weighting and sampledphase to the alreadyverified childdispatch, then validate finaloutput buffer/controlrouting foridentifiedPCrig. Reports ControllerState/live-post-blend-analysis.json and live-post-blend-source-matches.json. Existingcompletionbeep retained.
