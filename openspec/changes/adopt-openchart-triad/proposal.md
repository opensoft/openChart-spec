# Adopt the openChart triad

Brett Heap approved the concrete adoption plan and public leg creation on 2026-11-10.

The existing openChart repository becomes the assembly root. Contracts, ideation,
OpenSpec and Speckit specifications belong in openChart-spec. Implementation,
tests, Docker tooling and packaging belong in openChart-code.

Preserve extracted history, the existing recovery worktree and its local files.
Keep existing downstream xFactory and MedxChart pins. Update contract readers,
live evidence placement and root validation commands for the leg boundaries.

Implementation is tracked in specs/002-triad-adoption/tasks.md.
