# Embedded Control Example

This directory will host the first domain-specific Spec2Exec example after the minimal language/runtime proof of concept.

Candidate semantics:

```text
control_task.period = 1 ms
control_task.deadline = 800 us

pendulum_angle:
  type = float32
  unit = rad
  range = [-pi, pi]

motor_command:
  type = float32
  range = [-1, 1]
  safe_value = 0

failure:
  condition = encoder_invalid for >= 3 cycles
  transition = FAULT
  action = motor_command := safe_value
```

The purpose is to test whether timing, units, ranges, state transitions, and fail-safe behavior can survive synthesis as first-class semantics rather than comments in generated code.
