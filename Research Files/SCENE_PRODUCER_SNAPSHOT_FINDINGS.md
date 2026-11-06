# Bound matrix producer snapshot — 2026-10-20

`ce_sceneproducers_20261020_213724_165902671.json` reports all 14 expected hand/finger slots still point to their captured nodes. Producer RTTI and execute slots resolve to the already known Transform-to-matrix 55DA50 and Dilation-to-matrix 4DEE10 routines, rather than an unknown updater.

However the captured node payloads remain identity matrices with zero node evaluation stamps. The earlier binding capture also observed no matching live post-conversion outputs. The 62-slot object's references may therefore be template/inactive data or may be replaced/copied along an unobserved instancing path. This is a hypothesis, not proof of object purpose. It does not establish renderer parity or Elsa actor identity.

Next investigate active instances/reference connections to these nodes, not another replay of the same math. The new bounded CE read-only bridge allows subsequent pointer/header reads and explicit-range searches without repeated one-shot scripts. Initial live bridge verification is pending. Windows command-process reads were denied (error 5); the bridge uses CE's existing attachment and performs no memory writes.
