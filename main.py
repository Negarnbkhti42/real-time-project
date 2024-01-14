import csv
from models import processor as p
from models import task as t
import task_generator as tg

AVAILABLE_PERIODS = [10, 20, 40, 50]

core_utilization = float(input("Enter utilization of each core: "))
num_of_cores = int(input("Enter number of cores: "))
num_of_tasks = int(input("Enter number of tasks: "))
assignment_method = input("Enter assignment method (wfd or ffd): ")

task_set = tg.generate_tasks(
    num_of_tasks * core_utilization, num_of_tasks, AVAILABLE_PERIODS)

processor = p.Processor(num_of_cores, core_utilization)
assigned_tasks = processor.assign_tasks(task_set, assignment_method)


mock_cores = [0 for _ in range(8)]

with open(f'{num_of_cores}_cores_{core_utilization}_utilization_wfd_assign.csv', 'w', newline='', encoding="UTF-8") as file:
    writer = csv.writer(file)
    writer.writerow(["task", "utilization", "period",
                    "criticality", "assigned core", "core utilization"])
    for i, task in enumerate(assigned_tasks):
        assigned_core_number = task.assigned_core.number
        mock_cores[assigned_core_number - 1] += task.utilization
        writer.writerow([task.name, task.utilization, task.period, "high" if task.criticality ==
                        t.TASK_PRIORITIES["high"] else "low", task.assigned_core.number, mock_cores[assigned_core_number - 1]])
