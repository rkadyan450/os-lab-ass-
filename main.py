#!/usr/bin/env python3
"""Integrated OS Resource Management and Scheduling Simulator."""
from dataclasses import dataclass
from pathlib import Path
import logging
import math

LOG_FILE = Path(__file__).with_name("activity.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")

@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0

def nonnegative_int(prompt, minimum=0):
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if value < minimum:
                print(f"Enter an integer >= {minimum}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Enter a whole number.")
            logging.warning("Invalid integer input for prompt %r: %r", prompt, raw)

def read_processes():
    n = nonnegative_int("Number of processes (1-20): ", 1)
    if n > 20:
        raise ValueError("At most 20 processes are supported in this demo.")
    processes = []
    seen = set()
    for i in range(n):
        print(f"Process {i+1}")
        pid = input("  ID (e.g. P1): ").strip() or f"P{i+1}"
        if pid in seen:
            raise ValueError("Process IDs must be unique.")
        seen.add(pid)
        arrival = nonnegative_int("  Arrival time: ")
        burst = nonnegative_int("  Burst time (>0): ", 1)
        priority = nonnegative_int("  Priority (lower number = higher priority): ")
        processes.append(Process(pid, arrival, burst, priority))
    return processes

def schedule(processes, algorithm, quantum=2):
    """Non-preemptive FCFS/SJF/Priority and preemptive Round Robin."""
    if not processes:
        raise ValueError("At least one process is required.")
    if any(p.burst <= 0 or p.arrival < 0 for p in processes):
        raise ValueError("Burst must be > 0 and arrival must be >= 0.")
    remaining = {p.pid: p.burst for p in processes}
    first_start, completion = {}, {}
    timeline = []
    now = 0
    if algorithm == "Round Robin":
        if quantum <= 0:
            raise ValueError("Time quantum must be positive.")
        ready = []
        arrivals = sorted(processes, key=lambda p: (p.arrival, p.pid))
        idx = 0
        while len(completion) < len(processes):
            while idx < len(arrivals) and arrivals[idx].arrival <= now:
                ready.append(arrivals[idx]); idx += 1
            if not ready:
                if idx < len(arrivals):
                    now = arrivals[idx].arrival
                    continue
                break
            p = ready.pop(0)
            first_start.setdefault(p.pid, now)
            run = min(quantum, remaining[p.pid])
            timeline.append((p.pid, now, now + run))
            now += run
            remaining[p.pid] -= run
            while idx < len(arrivals) and arrivals[idx].arrival <= now:
                ready.append(arrivals[idx]); idx += 1
            if remaining[p.pid] > 0:
                ready.append(p)
            else:
                completion[p.pid] = now
    else:
        pending = list(processes)
        while pending:
            available = [p for p in pending if p.arrival <= now]
            if not available:
                now = min(p.arrival for p in pending)
                available = [p for p in pending if p.arrival <= now]
            if algorithm == "FCFS":
                p = min(available, key=lambda x: (x.arrival, x.pid))
            elif algorithm == "SJF":
                p = min(available, key=lambda x: (x.burst, x.arrival, x.pid))
            elif algorithm == "Priority":
                p = min(available, key=lambda x: (x.priority, x.arrival, x.pid))
            else:
                raise ValueError("Unknown scheduling algorithm.")
            start = now
            first_start[p.pid] = start
            now += p.burst
            timeline.append((p.pid, start, now))
            completion[p.pid] = now
            pending.remove(p)
    by_id = {p.pid: p for p in processes}
    rows = []
    for p in processes:
        tat = completion[p.pid] - p.arrival
        waiting = tat - p.burst
        response = first_start[p.pid] - p.arrival
        rows.append({"pid": p.pid, "arrival": p.arrival, "burst": p.burst,
                     "priority": p.priority, "completion": completion[p.pid],
                     "turnaround": tat, "waiting": waiting, "response": response})
    return rows, timeline

def print_schedule(rows, timeline, title):
    print(f"\n{title} results")
    print("PID  AT  BT  CT  TAT  WT  RT")
    for r in rows:
        print(f"{r['pid']:<4} {r['arrival']:>2}  {r['burst']:>2}  {r['completion']:>2}  "
              f"{r['turnaround']:>3}  {r['waiting']:>2}  {r['response']:>2}")
    print("Average waiting time: {:.2f}".format(sum(r["waiting"] for r in rows)/len(rows)))
    print("Average turnaround time: {:.2f}".format(sum(r["turnaround"] for r in rows)/len(rows)))
    print("Timeline: " + " | ".join(f"{pid}[{start}-{end}]" for pid,start,end in timeline))

def memory_first_fit(blocks, requests):
    """Allocate each request to first available block large enough; no splitting."""
    free = list(blocks)
    results = []
    for rid, size in enumerate(requests, 1):
        found = next((i for i, b in enumerate(free) if b >= size), None)
        if found is None:
            results.append({"request": rid, "size": size, "block": None, "waste": None})
        else:
            block = free[found]
            results.append({"request": rid, "size": size, "block": found + 1, "waste": block-size})
            free[found] = 0
    return results

def bankers_safety(available, allocation, maximum):
    """Banker's safety algorithm. Matrices are process rows, resource columns."""
    n, m = len(allocation), len(available)
    if len(maximum) != n or any(len(r) != m for r in allocation+maximum):
        raise ValueError("Allocation/maximum matrices must have matching dimensions.")
    if any(x < 0 for x in available):
        raise ValueError("Resource counts cannot be negative.")
    for i in range(n):
        for j in range(m):
            if allocation[i][j] < 0 or maximum[i][j] < allocation[i][j]:
                raise ValueError("Require 0 <= allocation <= maximum.")
    need = [[maximum[i][j]-allocation[i][j] for j in range(m)] for i in range(n)]
    work = available[:]
    finish = [False]*n
    sequence = []
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                work = [work[j]+allocation[i][j] for j in range(m)]
                finish[i] = True
                sequence.append(f"P{i}")
                changed = True
    return all(finish), sequence, need

def disk_fcfs(requests, head):
    if head < 0 or any(r < 0 for r in requests):
        raise ValueError("Head and requests must be non-negative.")
    order = [head] + list(requests)
    movement = sum(abs(order[i]-order[i-1]) for i in range(1, len(order)))
    return movement, order

def compare_schedulers(processes):
    output = {}
    for algo in ("FCFS", "SJF", "Priority", "Round Robin"):
        rows, timeline = schedule(processes, algo, quantum=2)
        output[algo] = {
            "avg_wait": sum(r["waiting"] for r in rows)/len(rows),
            "avg_turnaround": sum(r["turnaround"] for r in rows)/len(rows),
            "rows": rows, "timeline": timeline
        }
    return output

def menu():
    demo = [Process("P1",0,5,2), Process("P2",1,3,1), Process("P3",2,8,3), Process("P4",3,6,2)]
    while True:
        print("\n=== OS Resource Management Simulator ===")
        print("1. CPU scheduling (enter processes)")
        print("2. Memory allocation (First Fit)")
        print("3. Deadlock avoidance (Banker's safety check)")
        print("4. Disk scheduling (FCFS)")
        print("5. Compare CPU scheduling algorithms (demo dataset)")
        print("6. Exit")
        try:
            choice = input("Choose 1-6: ").strip()
            if choice == "1":
                ps = read_processes()
                algo = input("Algorithm (FCFS/SJF/Priority/Round Robin): ").strip()
                aliases = {"fcfs":"FCFS","sjf":"SJF","priority":"Priority","round robin":"Round Robin","rr":"Round Robin"}
                algo = aliases.get(algo.lower(), algo)
                q = nonnegative_int("Time quantum (used for Round Robin; enter 2 otherwise): ", 1)
                rows, timeline = schedule(ps, algo, q)
                print_schedule(rows, timeline, algo)
                logging.info("Ran scheduling algorithm %s on %d processes", algo, len(ps))
            elif choice == "2":
                blocks = [int(x) for x in input("Block sizes, space-separated (e.g. 100 500 200): ").split()]
                requests = [int(x) for x in input("Request sizes, space-separated (e.g. 90 210): ").split()]
                if not blocks or not requests or min(blocks+requests) <= 0:
                    raise ValueError("Enter non-empty lists of positive sizes.")
                print("Request  Size  Block  Unused space")
                for r in memory_first_fit(blocks, requests):
                    print(f"{r['request']:>7} {r['size']:>5}  {str(r['block'] or 'Not allocated'):>5}  {r['waste'] if r['waste'] is not None else '-'}")
                logging.info("Ran First Fit with %d blocks and %d requests", len(blocks), len(requests))
            elif choice == "3":
                available = [int(x) for x in input("Available resources, e.g. 3 3 2: ").split()]
                print("Enter allocation matrix rows (one row per process; space-separated).")
                allocation = [[int(x) for x in input(f"P{i} allocation: ").split()] for i in range(nonnegative_int("Process count: ",1))]
                maximum = [[int(x) for x in input(f"P{i} maximum: ").split()] for i in range(len(allocation))]
                safe, sequence, need = bankers_safety(available, allocation, maximum)
                print("Need matrix:", need)
                print("SAFE sequence:", " -> ".join(sequence) if safe else "No safe sequence (unsafe state)")
                logging.info("Ran Banker's safety check; safe=%s", safe)
            elif choice == "4":
                requests = [int(x) for x in input("Disk requests, space-separated (e.g. 98 183 37): ").split()]
                head = nonnegative_int("Initial head position: ")
                movement, order = disk_fcfs(requests, head)
                print("Service order:", " -> ".join(map(str, order)))
                print("Total head movement:", movement, "tracks")
                logging.info("Ran disk FCFS with %d requests", len(requests))
            elif choice == "5":
                result = compare_schedulers(demo)
                print("\nDemo dataset: P1(AT=0,BT=5,Pr=2), P2(1,3,1), P3(2,8,3), P4(3,6,2)")
                print("Algorithm       Avg waiting   Avg turnaround")
                for algo, values in result.items():
                    print(f"{algo:<15} {values['avg_wait']:>11.2f}   {values['avg_turnaround']:>14.2f}")
                logging.info("Compared all CPU scheduling algorithms on demo dataset")
            elif choice == "6":
                print("Goodbye.")
                break
            else:
                print("Choose a number from 1 to 6.")
                logging.warning("Invalid menu choice: %r", choice)
        except (ValueError, IndexError) as exc:
            print("Input error:", exc)
            logging.exception("Handled input/operation error")
        except KeyboardInterrupt:
            print("\nCancelled by user.")
            break

if __name__ == "__main__":
    menu()
