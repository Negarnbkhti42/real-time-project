import heapq
import csv
from models import task as t


def edf_vd_scheduling(tasks, num_cores, utilization, duration):
    active_tasks = []
    timeline = []
    time = 0
    while time < duration:  # Set a simulation time limit
        # Check for arrival of new tasks
        for task in tasks:
            if time % task.period == 0:
                heapq.heappush(active_tasks, t.Job(task))
                if task.criticality == 1:
                    for i in range(1, 4):
                        heapq.heappush(active_tasks, t.Job(task, i))

        # Check if there are tasks to execute
        if active_tasks:
            timestamp = []
            popped_tasks = []
            current_task = None
            for core in range(num_cores):
                # Get the task with the earliest deadline
                try:
                    current_task = heapq.heappop(active_tasks)
                except:
                    timestamp.append("")
                    continue

                # Execute the task on one of the cores
                timestamp.append(str(current_task))
                # Update remaining time
                current_task.remaining_exec_time -= 1

                # Check if the task is completed
                if current_task.remaining_exec_time == 0:
                    current_task.task.executed_jobs += 1

                else:
                    popped_tasks.append(current_task)

            for popped_task in popped_tasks:
                heapq.heappush(active_tasks, popped_task)

            timeline.append(timestamp)

        # Move to the next time step
        time += 1

    with open(f"schedule_{num_cores}_{utilization}.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([""] + ["Core " + str(i) for i in range(1, num_cores + 1)])
        for indx, timestamp in enumerate(timeline):
            writer.writerow([indx] + timestamp)

    return timeline
