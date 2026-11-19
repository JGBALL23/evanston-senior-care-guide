# ESCG Autonomous Loop Test

This is a controlled, non-production test of an event-triggered Claude routine.

- Current state: ARMED
- Test scope: two Claude runs maximum
- No production code, outreach messages, or social posts may be changed by this test
- Run 1: append `FIRST_RUN_COMPLETE` with a UTC timestamp and push the change to this branch
- Run 2: observe `FIRST_RUN_COMPLETE`, report `SECOND_RUN_TRIGGERED_AUTOMATICALLY`, and do not create further commits

The `FIRST_RUN_COMPLETE` marker must be written by the Claude event-triggered task, not by the setup operator.
