"""Optional chart generation: pip install -r requirements.txt, then python chart.py."""
from main import Process, compare_schedulers
import matplotlib.pyplot as plt

ps = [Process("P1",0,5,2), Process("P2",1,3,1), Process("P3",2,8,3), Process("P4",3,6,2)]
results = compare_schedulers(ps)
labels = list(results)
waiting = [results[a]["avg_wait"] for a in labels]
turnaround = [results[a]["avg_turnaround"] for a in labels]
x = list(range(len(labels)))
width = 0.36
plt.figure(figsize=(9, 5))
plt.bar([i-width/2 for i in x], waiting, width, label="Average waiting")
plt.bar([i+width/2 for i in x], turnaround, width, label="Average turnaround")
plt.xticks(x, labels)
plt.ylabel("Time units")
plt.title("CPU Scheduling Algorithm Comparison")
plt.legend()
plt.tight_layout()
plt.savefig("scheduler_comparison.png", dpi=160)
print("Saved scheduler_comparison.png")
