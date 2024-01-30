import csv
import math
import random
import numpy as np
from models import task as t


def generate_uunifastdiscard(u: float, n: int, filename: str):
    retries = 0
    while retries < 1000:
        utilizations = []
        sumU = u * 0.5
        for i in range(1, n):
            nextSumU = sumU * random.random() ** (1.0 / (n - i))
            utilizations.append(sumU - nextSumU)
            sumU = nextSumU
        utilizations.append(sumU)

        if all(ut <= 1 for ut in utilizations):
            with open(filename, "w", newline="", encoding="UTF-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Task " + str(i) for i in range(1, n + 1)])
                writer.writerow(utilizations)

            return utilizations

        retries += 1

    raise Exception("Could not generate utilization set")


def generate_tasksets(utilizations, periods):
    task_set = []

    break_point = len(utilizations) // 2

    for indx, u in enumerate(utilizations[:break_point]):
        task_period = random.choice(periods)
        wcet_multiplier = random.uniform(0.3, 0.5)
        wcet = round(u * task_period, 3)

        new_task = t.Task(
            indx,
            f"Task-{indx}",
            u,
            task_period,
            t.TASK_PRIORITIES["high"],
            round(wcet_multiplier * wcet, 3),
            wcet,
        )

        task_set.append(new_task)

        for i in range(1, 3):
            task_set.append(t.TaskCopy(new_task, i))

    for indx, u in enumerate(utilizations[break_point:]):
        real_indx = indx + break_point
        task_period = random.choice(periods)
        wcet = round(u * task_period, 3)

        task_set.append(
            t.Task(
                real_indx,
                f"Task-{real_indx}",
                u,
                task_period,
                t.TASK_PRIORITIES["low"],
                wcet,
                wcet,
            )
        )

    with open("task_set.csv", "w", newline="", encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "task",
                "utilization",
                "period",
                "relative deadline",
                "wcet",
                "criticality",
            ]
        )
        for i, task in enumerate(task_set):
            if not isinstance(task, t.TaskCopy):
                writer.writerow(
                    [
                        task.name,
                        task.utilization,
                        task.period,
                        task.relative_deadline,
                        f"{{{task.low_wcet}, {task.high_wcet}}}",
                        "high"
                        if task.criticality == t.TASK_PRIORITIES["high"]
                        else "low",
                    ]
                )

    return task_set


def generate_tasks(utilization: float, n: int, available_periods: list):
    task_set = []
    utilizations = []
    utilizations = generate_uunifastdiscard(
        u=utilization, n=n, filename="task_utilizations.csv"
    )

    task_set = generate_tasksets(utilizations, available_periods)

    return task_set


def dbf_by_core(task_set: list[t.Task], processor, hyper_period):
    for core in processor.cores:
        core_tasks = [task for task in task_set if task.assigned_core == core]
        demand_bound_function_tester(core_tasks, hyper_period)

def demand_bound_function_tester(task_set: list[t.Task], hyper_period):
    for i in range (0, hyper_period):
        demand = 0
        for task in task_set:
            demand += demand_bound_function(task, i)
        if demand > i:
            raise Exception("DBF failed")

def demand_bound_function(task: t.Task, x):
    maximal_jobs = max(0, 1 + math.floor((x - task.relative_deadline)/task.period))
    dbf = maximal_jobs * task.high_wcet
    return dbf
