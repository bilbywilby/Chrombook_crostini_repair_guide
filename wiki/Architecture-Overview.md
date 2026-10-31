# Architecture Overview

Crostini troubleshooting is easiest when performed from the outer layer inward:

1. **ChromeOS host:** Check host-level state and use crosh for `vmc` operations.
2. **Termina VM:** Check whether the Linux virtual machine is running and reachable.
3. **LXD container:** Check container state, Linux services, storage, and project diagnostics.

A failure at an outer layer can make inner-layer checks misleading. Establish which layer is responding before changing configuration.

## Resource guidance

The project resource-allocation guidance recommends allocating Termina RAM at approximately 50% of physical RAM and using 35 GB as a recommended LXD disk size. Treat these as starting recommendations, not universal requirements; available host resources and workload needs vary.

## Command boundaries

- Run `vmc` commands from ChromeOS crosh, not from the Linux container.
- Run `lxc` and the Python diagnostic procedures in their documented Linux environment.
- Review the effect of any shutdown, resize, or migration operation before proceeding.
