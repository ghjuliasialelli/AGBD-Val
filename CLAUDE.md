# Project: AGBD-Val — AGB map validation testbed

## Machine rule (pf-pc28) — WRITE LOCATION
**Always write to `/scratch3/gsialelli`. Never write anything under `/home/gsialelli`.**
- `/home/gsialelli` is over quota (`EDQUOT`) AND is off-limits by user instruction.
- Consequence: the Claude memory store (`/home/gsialelli/.claude/projects/.../memory/`), the plan-file
  dir, and `session-env` are all unusable. Persist project context in `/scratch3` instead — this file
  and `catalog/PROJECT_STATE.md`.
- The broken `/home` quota also disables the Bash tool here (it can't create its `session-env`). Use
  the `Read`/`Write` file tools (they work) and web tools; scripts can only be *run* once the quota is freed.

## What this repo is
A validation testbed for above-ground biomass (AGB) maps. First deliverable: a metadata catalog of
independent AGB reference data under `catalog/`. See `catalog/README.md` (schema + validation traps)
and `catalog/PROJECT_STATE.md` (full state / handoff).

## Scope (2026-07-23)
Global. Reference classes: **in-situ plots** + **airborne-lidar AGB** only. Spaceborne lidar
(GEDI/ICESat-2) and gridded intercomparison maps (CCI, Spawn, ...) deliberately excluded as
non-independent.

## Also follow the global geospatial playbook
`~/.claude/CLAUDE.md` (units Mg vs MgC vs m3; CRS/merge traps; per-axis intersection + assert n>0;
sample at pixel centres; south-up rasters; mask nodata on raw values; record mtime/hash of source rasters).
