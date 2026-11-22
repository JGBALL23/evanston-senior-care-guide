# ESCG loop tools

`ops/loopctl.py` is the small helper the ESCG worker uses to read and edit the loop state files
(what is due, locks, finishing tasks). Standard library only; it never touches the network.
The worker copies it from this branch if the state branch does not have it.
