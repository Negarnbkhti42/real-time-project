import csv
from models import processor as p
from models import task as t
import task_generator as tg

AVAILABLE_PERIODS = [10, 20, 40, 50, 100, 200, 400, 500, 1000]

core_utilization = float(input("Enter utilization of each core: "))
num_of_cores = int(input("Enter number of cores: "))
num_of_tasks = int(input("Enter number of tasks: "))
assignment_method = input("Enter assignment method (wfd or ffd): ")

task_set = tg.generate_tasks(
    num_of_cores * core_utilization, num_of_tasks, AVAILABLE_PERIODS
)

processor = p.Processor(num_of_cores, core_utilization)
assigned_tasks = processor.map_tasks(task_set, assignment_method)


mock_cores = [0 for _ in range(num_of_cores)]

with open(
    f"{num_of_cores}_cores_{core_utilization}_utilization_{assignment_method}_mapping.csv",
    "w",
    newline="",
    encoding="UTF-8",
) as file:
    writer = csv.writer(file)
    writer.writerow(
        [
            "task",
            "utilization",
            "period",
            "criticality",
            "assigned core",
            "core utilization",
        ]
    )
    for i, task in enumerate(assigned_tasks):
        assigned_core_number = task.assigned_core.number
        mock_cores[assigned_core_number - 1] += task.utilization
        writer.writerow(
            [
                task.name,
                task.utilization,
                task.period,
                "high" if task.criticality == t.TASK_PRIORITIES["high"] else "low",
                task.assigned_core.number,
                mock_cores[assigned_core_number - 1],
            ]
        )

schedules = processor.schedule_tasks(assigned_tasks, 4000)

with open(
    f"{num_of_cores}_cores_{core_utilization}_utilization_{assignment_method}_scheduling.csv",
    "w",
    newline="",
    encoding="UTF-8",
) as file:
    writer = csv.writer(file)
    writer.writerow(["time", "core", "task", "job"])
    for time, timeslot in enumerate(schedules):
        for core in timeslot:
            writer.writerow(
                [
                    time / 1000,
                    core["core"],
                    core["task"],
                    core["job"],
                ]
            )
