# OS Resource Management and Scheduling Simulator

A single integrated Python CLI application demonstrating four Operating Systems concepts:
- CPU scheduling: FCFS, non-preemptive SJF, non-preemptive Priority, Round Robin
- Memory allocation: First Fit
- Deadlock avoidance: Banker's safety algorithm
- Disk scheduling: FCFS head movement
- CPU algorithm comparison, test suite, activity log, and chart-generation helper

## Requirements
- Python 3.9+
- No third-party packages are required to run `main.py` or tests.
- Optional chart generation requires Matplotlib (`pip install -r requirements.txt`).

## Run
```bash
python main.py
```
Select menu items 1–6. Menu item 5 compares the CPU algorithms on a built-in dataset. Activity is recorded in `activity.log`.

## Run tests
```bash
python -m unittest -v
```

## Generate comparison chart
```bash
python chart.py
```
This writes `scheduler_comparison.png` using the same sample dataset.

## Sample CPU dataset
| Process | Arrival | Burst | Priority (lower is higher) |
|---|---:|---:|---:|
| P1 | 0 | 5 | 2 |
| P2 | 1 | 3 | 1 |
| P3 | 2 | 8 | 3 |
| P4 | 3 | 6 | 2 |

Round Robin uses quantum 2. Metrics: CT = completion time, TAT = CT − arrival time, WT = TAT − burst time, RT = first start − arrival time.

## Sample interactions
Memory First Fit:
- Blocks: `100 500 200`
- Requests: `90 210 600`
- Expected: request 90 -> block 1 (10 unused); request 210 -> block 2 (290 unused); request 600 -> not allocated.

Disk FCFS:
- Requests: `98 183 37 122 14 124 65 67`
- Initial head: `53`
- Expected total head movement: `640 tracks`.

Banker's algorithm:
- Available: `3 3 2`
- Allocation rows: `0 1 0`; `2 0 0`; `3 0 2`; `2 1 1`; `0 0 2`
- Maximum rows: `7 5 3`; `3 2 2`; `9 0 2`; `2 2 2`; `4 3 3`
- Expected state: SAFE; one valid sequence is P1 -> P3 -> P4 -> P0 -> P2 (sequence ordering can vary based on scan order).

## Project structure
```text
os_resource_management_simulator/
├── main.py
├── test_main.py
├── chart.py
├── README.md
├── REPORT.md
├── SAMPLE_OUTPUT.txt
├── requirements.txt
├── screenshots/
│   ├── menu.png
│   └── comparison.png
└── activity.log  (created at runtime)
```

## Design notes and limitations
This is an educational simulator, not a real kernel scheduler. SJF and Priority are non-preemptive; Round Robin is preemptive. First Fit treats each block as a single-use fixed partition and does not split blocks or model compaction. Disk scheduling implements FCFS only. The menu validates key values and catches common input errors. Banker's algorithm validates matrix dimensions and allocation/maximum consistency.
