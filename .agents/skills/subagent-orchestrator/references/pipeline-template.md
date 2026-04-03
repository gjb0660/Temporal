# Stage Pipeline Template

Use this skeleton to define a decision-complete execution timeline.

## Global Contract

- Enforce serial stage boundaries.
- Open parallel work only inside stage execution windows.
- Close stage with supervisor-only convergence and atomic commit.
- Run stage-sync before admitting the next stage.

## Stage Blueprint

### Stage <N>: <Name>

#### Entry Gate (serial)

1. Confirm stage objective and non-goals.
2. Freeze ownership boundaries.
3. Freeze acceptance criteria.
4. Capture pollution baseline.

#### Parallel Window

- Agent A ownership: <files/modules>
- Agent B ownership: <files/modules>
- Agent C ownership: <files/modules>

Rules:

- No cross-ownership edits.
- No bypass of required checks.
- No new out-of-scope work.

#### Convergence (serial)

1. Validate acceptance mapping from each agent.
2. Validate pollution delta against baseline.
3. Validate overlap and semantic consistency.
4. Resolve conflicts serially if needed.

#### Stage Close (serial)

1. Run full gate profile.
2. Perform one supervisor atomic commit.
3. Run stage-sync checkpoint across all agents.
4. Admit or block next stage.

## Stage Cluster Option

Use stage cluster merge for tightly coupled sub-stages:

- Keep sub-stage gates explicit.
- Produce one atomic commit at cluster close.
- Do not bypass cluster-level full gate and stage-sync.
