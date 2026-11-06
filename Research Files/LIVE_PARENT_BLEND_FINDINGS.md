# Live parent blend findings — 2026-10-20 00:05

Capture ce_parentblend_20261020_000528_88387578.jsonl:24left-before/24left-after/24right-before/24right-after,96eventlimit;141rawhits per site.48pairednativeblend calls all byte-exact across5376destinationrows. No rejectedpairs. Allmode1;leftweight1 in24pairs;rightweightsvary through24interpolatedcases (including approximately.01702,.04241,.25230,.41594,.60750,.79075,.95609,.97613,.99999). Selectedchild,side,parent,weight/alpha,childmode,stack+12,depthpop anddestinationidentity checks pass.

analyze_parent_blend_chains.py joins24left/right chains byparent/manager/pre-callstack andorderedobservations. All24haveidenticalleft-result/right-inputbytes,samedestinationframe/pointer/extent,andunchangedparentselection. Replaying both native5A14D0 stages insequencefromleftinitial andcapturedsources matchesrightfinal BYTE-FOR-BYTE for all24chains. No chainboundaries. This is strongerthan independentcallmatches, but stilldoesnotprove threadidentity or finalrigconsumption.

Negativefixture alters rightinitialbuffer and recomputes rightfinal natively, preserving individualpairvalidity. Chainchecker correctlyrejects changedintermediatestage. This testsactualcontinuity ratherthan merelyrepeatingoperatorchecks.

Reports ControllerState/live-parent-blend-analysis.json,live-parent-blend-chain-analysis.json and.pairs.json companion,parent-blend-chain-analyzer-validation.json. Earlierfile-sample,time,selector andchildblendcapturesremainseparateevidence, not afulluninterruptedactorreconstruction. No viewerposeoffsets orcompositionchanges.

Next: trace how completedcombinedclipbuffer is emitted tocontroller source nodes/finalrigcontrols, verify mapping/masks andfinalvalues beforedeclaring1:1preview. Existingcapturecompletionbeep retained.
