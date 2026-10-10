# Project Report: OS Resource Management and Scheduling Simulator

## 1. Abstract
This project implements an integrated command-line simulator for core Operating Systems resource-management concepts. It combines CPU scheduling, fixed-block memory allocation, deadlock safety analysis, disk request servicing, algorithm comparison, logging, and automated tests in one Python application.

## 2. Problem statement
Operating Systems coordinate CPU time, memory, shared resources, and storage I/O. The project provides a small interactive environment to demonstrate how common algorithms behave on supplied inputs and to compare scheduling metrics.

## 3. Objectives
- Build modular, reusable functions for major OS concepts.
- Accept user inputs through one menu-driven program.
- Calculate scheduling metrics and total disk-head movement.
- Check resource-allocation states using the Banker's safety algorithm.
- Validate inputs, log operations, and test normal and invalid cases.
- Document reproducible execution steps and observations.

## 4. Architecture and data flow
`User -> Menu/input validation -> Selected algorithm module -> Results/table -> activity.log`

- `Process` dataclass stores PID, arrival time, burst time, and priority.
- `schedule()` calculates completion, turnaround, waiting, response times, and timeline.
- `memory_first_fit()` allocates each request to the first available sufficiently large block.
- `bankers_safety()` calculates Need = Maximum − Allocation and searches for a safe sequence.
- `disk_fcfs()` computes total movement between consecutive head positions.
- `compare_schedulers()` evaluates four scheduling algorithms on the same workload.
- `test_main.py` verifies core behavior and boundary/error cases.

## 5. Algorithms
- **FCFS:** processes run in arrival order.
- **SJF:** among ready processes, the shortest burst runs next (non-preemptive).
- **Priority:** among ready processes, the lowest numeric priority runs next (non-preemptive).
- **Round Robin:** ready processes receive at most a fixed time quantum per turn.
- **First Fit:** each memory request takes the first unused block large enough.
- **Banker's safety:** repeatedly completes any process whose remaining Need can be met by current Work.
- **Disk FCFS:** services requests in the entered order.

## 6. Metrics
For each process: `Turnaround = Completion − Arrival`; `Waiting = Turnaround − Burst`; `Response = First start − Arrival`. The comparison prints average waiting and turnaround times. Disk movement is the sum of absolute differences between successive head positions.

## 7. Testing and reliability
Run `python -m unittest -v`. Tests cover FCFS metrics, SJF selection, Round Robin completion, invalid quantum, First Fit allocation failure, safe and invalid Banker matrices, disk movement, and comparison output. Interactive input errors are caught and logged to `activity.log`.

## 8. Demonstration and sample results
Use menu option 5 for the built-in CPU workload. Use option 2 with blocks `100 500 200` and requests `90 210 600`; the final request is not allocated. Use option 4 with head 53 and requests `98 183 37 122 14 124 65 67`; total movement is 640 tracks. Use the Banker's example in the README to observe a safe state.

## 9. Observations
Different scheduling policies can change average waiting and turnaround time for the same workload. SJF often lowers average waiting time when short jobs are available, while Round Robin improves the opportunity for each ready process to receive CPU time. First Fit is simple but can leave unusable gaps; Banker's algorithm avoids granting resources into an unsafe state when its assumptions hold.

## 10. Conclusion
The project integrates multiple OS concepts in a single menu-driven Python program with reusable functions, input checks, test cases, logging, and documentation. It is suitable as a learning demonstration; it does not simulate hardware or replace a real operating-system scheduler.
