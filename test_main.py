import unittest
from main import Process, schedule, memory_first_fit, bankers_safety, disk_fcfs, compare_schedulers

class TestOSSimulator(unittest.TestCase):
    def setUp(self):
        self.ps = [Process("P1",0,5,2), Process("P2",1,3,1), Process("P3",2,8,3), Process("P4",3,6,2)]

    def test_fcfs_completion_and_metrics(self):
        rows, timeline = schedule([Process("P1",0,4), Process("P2",1,3)], "FCFS")
        self.assertEqual([r["completion"] for r in rows], [4,7])
        self.assertEqual([r["waiting"] for r in rows], [0,3])

    def test_sjf(self):
        rows, _ = schedule([Process("P1",0,7), Process("P2",0,2)], "SJF")
        self.assertEqual(rows[1]["completion"], 2)

    def test_round_robin(self):
        rows, timeline = schedule([Process("P1",0,5), Process("P2",0,3)], "Round Robin", 2)
        self.assertEqual({r["pid"] for r in rows}, {"P1","P2"})
        self.assertEqual(max(end for _,_,end in timeline), 8)

    def test_invalid_quantum(self):
        with self.assertRaises(ValueError):
            schedule([Process("P1",0,1)], "Round Robin", 0)

    def test_memory_first_fit(self):
        got = memory_first_fit([100,500,200], [90,210,600])
        self.assertEqual([x["block"] for x in got], [1,2,None])

    def test_bankers_safe(self):
        available = [3,3,2]
        allocation = [[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]
        maximum = [[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]]
        safe, seq, need = bankers_safety(available, allocation, maximum)
        self.assertTrue(safe)
        self.assertEqual(len(seq), 5)

    def test_bankers_invalid_matrix(self):
        with self.assertRaises(ValueError):
            bankers_safety([1], [[2]], [[1]])

    def test_disk_fcfs(self):
        movement, order = disk_fcfs([98,183,37,122,14,124,65,67], 53)
        self.assertEqual(movement, 640)
        self.assertEqual(order[0], 53)

    def test_compare(self):
        result = compare_schedulers(self.ps)
        self.assertEqual(set(result), {"FCFS","SJF","Priority","Round Robin"})

if __name__ == "__main__":
    unittest.main(verbosity=2)
