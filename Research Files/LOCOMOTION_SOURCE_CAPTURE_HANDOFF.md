# Locomotion source route probe — 2026-10-19

Prior generic4E3FA6 capture identifies passive-idle source prefix/scalars, but does not reveal all native motion graph routes. New DI3_LocomotionSourceLogger.lua observes three SHA-pinned instruction sites using hardware execution breakpoints:

-543F40 ClipProcessor sample entry:ECXprocessor; processor+3Casset -> asset+3CClipDataBlock, first256bytes; time node+18,mapping+48 recorded. Static sampler52B720 proves asset+3Cread. Time node payload not interpreted or forced.
-5A1611 group evaluator before call5A14D0:ECXbuffer manager,ESIchild; stack contains weightfloat,mode,filter pointer. Child raw64byteheader/RTTIcandidate. No virtual getter execution or assumed source filename.
-5A14D0 buffer dispatcher entry:ECXmanager,returncaller and stack weight/mode/filter captured. Distinguishes othercallers from traced group site; call order alone is not nesting or actor identity.

First4calls per object/kind (and child for group) accepted,96total/10seconds,rawhitcounters retained. This reduces repeat saturation but can still include other actors and does not ensure every source is seen. Three12byte signatures verified before installation; PE32/ASLRguard, empty breakpoint list, olderloggerunload, F8/F9 lifecycle and partialinstallcleanup retained. Beeps once after successful completion; silent on arming/setupfailure/unload. No game writes,injection or forcedevaluation.

Three actual Lua5.3 mock cases pass: normal bounded repeatedcalls/sourceprefix/rawcounts/beep, badsignature and partialinstallationcleanup. Live behavior unverified. Prefix matcher accepts new clip_sample events and searches106 extracted fileblocks as candidates only; no full live allocation/hash proof.

Run DI3_LocomotionSourceLogger.lua, start Elsa moving forward,pressF8,keepmoving untilcompletionbeep,send ce_locosource_*.jsonl. This replaces the genericinputprobe for the next experiment. Viewer unchanged.

## Live locomotion-route capture — 2026-10-19 22:16
ce_locosource_20261019_221612_81831968.jsonl reached10secondlimit,40accepted records:24clip_sample,8group_dispatch,8buffer_dispatch. Rawhits2729/1242/1242 show allthree routes active; acceptedcalls are quota-limited, not actual totalexecution counts. Six sampler objects/sourceprefixes, candidates include elsa_bm_idle_specific03.oct andbiped_bm_idle_active_eyes.oct; fourunknown within106blockcatalog. Specific03 is not oneofcurrentfourviewerprofiles. Its extracted5.0333333secondclip contains varying left/right handchannels, unlike constant checkedprofiles, but no livephase/scalarjoin toearliercapture established.

Two group bufferobjects/twochild ReferencedTrack RTTIcandidates captured. All8grouprecords weight1,mode1,filternull;8bufferentryrecords sameargumentpattern withcallerrebasedto5A1616. This is boundedrouteevidence, not nestedcall/thread/actoridentityproof. No walk/runprefix candidate seen. Do not infer gamecharacter didnotmove.

Probe review found first4calls per samplerobject could suppress later assetchanges. Updated quota identity includes object+asset+blob, so a laterdifferent source getsitsownfourrecords while total96/10sec limitsremain. Quota stilldoesnotcapturefullphasehistory. Mocknormal/signature/partialcleanupcasespass;completionbeepretained. Viewerunchanged.

Reports live-locomotion-source-analysis-221612.json and.prefixes.json; analyzer explicitlyqualifiesmissingphase/actoridentity. Nextcapturecanstartbrieflyidlethenrunforwardtoobserve sourcechanges usingrevisedquota,ratherthanassumingearlysource staysactive throughout10seconds.

## Live transition capture — 2026-10-19 22:18
Capture ce_locosource_20261019_221847_81986640.jsonl completed at the ten-second limit with 68 records: 52 clip samples, eight group dispatches and eight buffer dispatches. Raw breakpoint hits: 2857 / 1240 / 1240 respectively. Thirteen object/source pairs captured; prefix candidates include idle_specific01, idle_passive, idle_specific02 and active_eyes. Nine prefixes remain unmatched in the bounded extracted catalog, rather than proven invalid.

Sampler 0x0911F190 first observed specific01 at 63 ms, passive idle at 516 ms, and specific02 at 7063 ms. This proves the revised per-object/asset/blob quota records changed sources on a reused sampler. First observations do not prove continuous execution or exact transition times. No walk/run prefix candidate identified. Group samples retain ReferencedTrack RTTI candidate, weight 1, mode 1, null filter. Viewer unchanged.

Added first-observed source timeline and explicit output path to analyze_locomotion_source_capture.py. Reports: ControllerState/live-locomotion-source-analysis-221847.json and its .prefixes.json companion. Asked user whether Elsa visibly ran during this capture; this distinction matters before selecting another probe. Do not infer that the character stayed idle merely from this subset of source routes, and do not request another identical run without resolving observation versus actor/graph routing.

## Capture 2026-10-19 22:22
ce_locosource_20261019_222248_82228000.jsonl: 54 accepted records (38 native clip samples, eight group dispatches, eight buffer dispatches), ten-second timer completion. Raw hits: 2471 sampler, 1226 group and 1226 dispatcher. Ten distinct object/source pairs. Prefix candidates: passive idle first observed62ms, idle_specific01 at875ms on sampler0911F190; eye idle at218ms on0911F430. Seven prefixes unmatched in current106block extracted catalog; do not infer invalid data. All recorded dispatch arguments weight1/mode1/nullfilter. No known walk/run source prefix observed.

Asked whether Elsa visibly ran in this latest capture. Previous user confirmation of remaining idle applies to the earlier22:18 run, not automatically this file. If latest was visibly running, investigate actor/path selection or uncatalogued motion sources; if idle, obtain confirmed moving input before interpreting absence. Do not blindly repeat the same capture or change viewer composition based on missing prefix matches. No viewer changes.

Reports ControllerState/live-locomotion-source-analysis-222248.json and its.prefixes.json companion. First-observed timestamps and quota limitations remain qualified.

## Changed group route — capture 2026-10-19 22:24
ce_locosource_20261019_222429_82329031.jsonl reaches96eventlimit at2187ms.18sampler,66group,12bufferentry records. Five standalone sampler source prefixes unmatched in extracted catalog. Group records:62 ReferencedTrack and4 KeyBlendTrack RTTI candidates.38group calls weight1/mode1,18weight1/mode0,eightweight0.899999976/mode1,twoweight0.850000024/mode1; allnullfilter. Bufferentryquota captures11mode1 andonemode0. Unlike idle-only captures, multiple weighted children andbothdispatch modes observed. This is route evidence, not verified actor identity or walk/run file identification.

RTTI vtable1B38EC4+24 resolves ReferencedTrack execute59FBB0. It calls sampler59EB40 at59FC6E. Sampler59EB50 reads track+28 asset,59EB53 reads asset+3C ClipDataBlock. Thus native group tracks can read source data without543F40 ClipProcessor entry. Previous source-prefix hook missed this independent path.

Updated locomotionlogger group record: only exact ReferencedTrack RTTI candidate permits child+28 -> asset+3C, first256bytes. No additionalbreakpoint,write,injection or forcedevaluation;96/10sec bounds andbeep retained. Prefixmatcher nowaccepts referenced group source snapshots. Normal mock explicitlychecksnewpointerchain/prefixwidth;signaturefailure andpartialcleanup stillpass. Next run uses same updatedlogger to identify group source file candidates; no viewer changes until identified and joined to control data.

Reports ControllerState/live-locomotion-source-analysis-222429.json and.prefixes.json preserve this capture. Prior22:22 capture was confirmed idle byuser; latest22:24 visiblemovement not yetexplicitlyconfirmed, so avoid claiming it proves locomotion.
