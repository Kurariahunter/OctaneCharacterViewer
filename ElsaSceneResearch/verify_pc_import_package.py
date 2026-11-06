import hashlib,json
from pathlib import Path
r=Path('F:/DisneyInfinityPortalTest/ElsaSceneResearch');cache=Path('C:/Users/Kurar/Disney Reloaded/Library/DI3ZipCache/a83da00a4dcb40c2bf80eaa8bfda96ae');rows=[]
checks=[('fro_elsa.oct',r/'InstalledGameAssetCheck/fro_elsa/fro_elsa.oct'),('characters/fro_elsa/motions/elsa_bm_idle_active.oct',r/'InstalledGameAssetCheck/IdleMotions/fro_elsa/characters/fro_elsa/motions/elsa_bm_idle_active.oct'),('characters/fro_elsa/motions/elsa_bm_idle_passive.oct',r/'InstalledGameAssetCheck/IdleMotions/fro_elsa/characters/fro_elsa/motions/elsa_bm_idle_passive.oct'),('fro_elsa.bent',r/'InstalledGameAssetCheck/Bent/fro_elsa/fro_elsa.bent')]
for relative,installed in checks:
 p=cache/relative
 row={'file':relative,'cache_exists':p.exists()}
 if p.exists():
  sha=hashlib.sha256(p.read_bytes()).hexdigest();row.update(sha256=sha,exact_installed_match=sha==hashlib.sha256(installed.read_bytes()).hexdigest())
 rows.append(row)
print(rows)
report={'scope':'Archive contains converted Unity assets and reports, not raw game OCTs. Import report points to an existing cache; inspected that cache read-only and verified selected raw assets against our installed-game extraction. Package source association is supported by report paths, not a raw OCT embedded in the7z.','archive':'C:/Users/Kurar/Disney Reloaded/Assets/DI3Converted/fro_elsa_3.0_PC.7z','import_report_counts':{'vertices':5419,'triangles':8935,'bones':62},'checks':rows,'remaining':'Converted prefab is a static/bind rig with approximate helper parenting, not a completed original-animation reconstruction. Eye import unsupported in report. Preserve package as matching PC mesh/material reference; integrate reconstructed procedural animation separately.'}
(r/'pc-import-package-verification.json').write_text(json.dumps(report,indent=2))
