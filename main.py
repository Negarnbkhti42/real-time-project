import csv
import matplotlib.pyplot as plt
from models import processor as p
from models import task as t
import task_generator as tg
from config import DEBUG
AVAILABLE_PERIODS = [100, 150, 300]

number_of_sets = int(input("Enter number of task sets: "))
core_utilization = float(input("Enter utilization of each core: "))
num_of_cores = int(input("Enter number of cores: "))
num_of_tasks = int(input("Enter number of tasks: "))
assignment_method = input("Enter assignment method (wfd or ffd): ")
scheduling_method = input("Should edf-vd be used?(y/n) ")
scheduling_method = "edf-vd" if scheduling_method == "y" else "edf"
overrun_rate = float(input("Enter overrun rate: "))

test_results = []
quality_of_services = []
num_of_success = 0
num_of_fail = 0
for i in range(number_of_sets):
    test_results.append(num_of_success)
    # num_of_tasks = 10*i + 5
    try:
        print("round", i + 1)
        task_set = tg.generate_tasks(
            num_of_cores * core_utilization, num_of_tasks, AVAILABLE_PERIODS
        )

        processor = p.Processor(num_of_cores, core_utilization)
        assigned_tasks = processor.map_tasks(task_set, assignment_method)
        tg.dbf_by_core(task_set, processor, max(AVAILABLE_PERIODS))
        mock_cores = [0 for _ in range(num_of_cores)]

        if DEBUG:
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

        schedules, QoS = processor.schedule_tasks(
            assigned_tasks, max(AVAILABLE_PERIODS), overrun_rate, scheduling_method
        )

        quality_of_services.append(QoS)

        if DEBUG:
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
                    row = [time]
                    timeslot.sort(key=lambda x: x["core"])

                    for core in timeslot:
                        row.append(f'{core["job"]}{"(overrun)" if core["overrun"] else ""}')

                    writer.writerow(row)

        num_of_success += 1
    except Exception as e:
        print(e)
        if DEBUG:
            raise e
        if not str(e).__contains__("fit"):
            print("fail")
            num_of_fail += 1
            continue
print(f"success: {num_of_success}, fail: {num_of_fail}")
print("quality of service: ", quality_of_services)
# plt.hist(quality_of_services)

# plt.savefig(
#     f"{num_of_cores}_cores_{core_utilization}_utilization_{assignment_method}_{scheduling_method}_scheduling.png"
# )


import matplotlib.pyplot as plt

arr = test_results

plt.plot(arr)
plt.xlabel('number of tests')
plt.ylabel('success')
plt.title('successful scheduling')
plt.show()

arr = quality_of_services

plt.plot(arr)
plt.xlabel('number of tests')
plt.ylabel('QoS')
plt.title('Sum of Elements of an Array')
plt.show()