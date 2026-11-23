# Test copy, not production

Copies of ops/cloud.json, ops/growth.json and ops/state.json from `ops/operator-state`, made on 22 Nov 2026
to rehearse the Make-controlled worker. Nothing reads this branch except those tests.

## 23 Nov 2026 18:10Z: Make chain test
Copied from ops/operator-state at that time. Planner and sweep angles disabled, open map items set to watch, scouts deferred, five ready SYS-T tasks. With Mode "Smoke test" a session works at most 3 tasks, so it must report next yes and Make must start the next session, which works the last 2.
