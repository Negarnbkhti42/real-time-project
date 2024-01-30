import csv
from models import processor as p
from models import task as t
import task_generator as tg

AVAILABLE_PERIODS = [10, 20, 25, 50, 100, 200, 250, 500, 1000]

core_utilization = float(input("Enter utilization of each core: "))
num_of_cores = int(input("Enter number of cores: "))
num_of_tasks = int(input("Enter number of tasks: "))
assignment_method = input("Enter assignment method (wfd or ffd): ")
scheduling_method = input("Should edf-vd be used?(y/n) ")
scheduling_method = "edf-vd" if scheduling_method == "y" else "edf"
overrun_rate = float(input("Enter overrun rate: "))

task_set = tg.generate_tasks(
    num_of_cores * core_utilization, num_of_tasks, AVAILABLE_PERIODS
)

processor = p.Processor(num_of_cores, core_utilization)
assigned_tasks = processor.map_tasks(task_set, assignment_method)
tg.dbf_by_core(assigned_tasks, processor, 1000)


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

schedules = processor.schedule_tasks(assigned_tasks, 1000, overrun_rate, scheduling_method)

with open(
    f"{num_of_cores}_cores_{core_utilization}_utilization_{assignment_method}_{scheduling_method}_scheduling.csv",
    "w",
    newline="",
    encoding="UTF-8",
) as file:
    writer = csv.writer(file)
    header = ["time"]
    for i in range(num_of_cores):
        header.append(f"core {i + 1}")

    writer.writerow(header)

    for time, timeslot in enumerate(schedules):
        row = [time / 1000]
        timeslot.sort(key=lambda x: x["core"])

        for core in timeslot:
            row.append(f'{core["job"]}{'(overrun)' if core["overrun"] else ''}')

        writer.writerow(row)
