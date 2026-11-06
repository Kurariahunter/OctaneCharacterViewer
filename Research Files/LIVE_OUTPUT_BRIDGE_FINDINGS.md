# Live buffer-to-node bridge findings — 2026-10-20 00:14

Capture ce_outputbridge_20261020_001449_88948609.jsonl completed at ten-second limit with21before/21after pairs;2075rawhits at eachsite. All21supportedtyped replays match payload bytes AND node stamps exactly,zero rejectedpairs/mismatches.1455supportednodeobservations:882Transform64 and573Float4.66nulloutputslots and9EventSetunknownpayloadslots explicitly omitted. No liveDilation32outputnode observed inthiscapture; syntheticDilationfixturecoverage mustnot be mislabeled live.

Processors090BCA00 and091DCE80 have112row biped-sized streams (six andthree acceptedcalls). Each contains60genericTransform,45Float,sixnulloutputs,oneEventSet. Processors091D8F40/09257640 have42/45rows,sixcalls each; these mixedstreams remaindistinct. GenericTransform outputs can stand infor controls represented asDilation inthe authoredrig; this is not yet finalrigconsumption. Native typedpredicateglobals anddescriptorwords replayed exactly, avoiding assumed quaternion normalization behavior from type names alone.

Using file-derivedbiped LocalToPortIndices (withpriorbipedmappingevidence,butnot independentlycapturedinthisprobe),090BCA00 outputs matchall14currentforward-runpreview hand/thumb scalarvalues inall6calls (84exactcomparisons).091DCE80 matchesonly1/14percall andhasdifferenthandpose. Do not assume uniqueactoridentity,sourcepurpose,orwhichstreamwins laterblending. This narrows discrepancy towardstreamcombination/finalriginput ratherthan rootrunhanddecode.

Reports ControllerState/live-output-bridge-analysis.json,output-bridge-biped-hand-values.json,output-bridge-run-hand-comparison.json. Exactbridge validation connects blendedrows to genericcontrolleroutputnodes, not finalskinpalette. Earlierselector/time/childblend/parentblend checkpoints remainseparatelyqualified. Viewerunchanged,nohandposeoffsets.

Nexttracegenericoutputnode producers/consumers into finalFloat/Dilationriginputs andvalidatecontributorweights/mapping inmatchingrunningstate. Preserveotheractorstreams andEventSet boundaries.
