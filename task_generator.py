import csv
import random
import numpy as np
from models import task as t


def generate_uunifastdiscard(u: float, n: int, filename: str):
    retries = 0
    while retries < 1000:
        utilizations = []
        sumU = u
        for i in range(1, n):
            nextSumU = sumU * random.random() ** (1.0 / (n - i))
            utilizations.append(sumU - nextSumU)
            sumU = nextSumU
        utilizations.append(sumU)

        if all(ut <= 1 for ut in utilizations):
            with open(filename, 'w', newline='', encoding='UTF-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Task ' + str(i) for i in range(1, n+1)])
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

        new_task = t.Task(f"Task-{indx}", u / 3, task_period, t.TASK_PRIORITIES["high"], max(
            1, int(wcet_multiplier * task_period)), task_period)

        task_set.append(new_task)

        for i in range(1, 3):
            task_set.append(t.TaskCopy(new_task, i))

    for indx, u in enumerate(utilizations[break_point:]):
        real_indx = indx + break_point
        task_period = random.choice(periods)

        task_set.append(t.Task(
            f"Task-{real_indx}", u, task_period, t.TASK_PRIORITIES["low"], task_period, task_period))

    with open('task_set.csv', 'w', newline='', encoding='UTF-8') as file:
        writer = csv.writer(file)
        writer.writerow(["task", "utilization", "period",
                        "relative deadline", "wcet", "criticality"])
        for i, task in enumerate(task_set):
            if not isinstance(task, t.TaskCopy):
                writer.writerow([task.name, task.utilization, task.period, task.relative_deadline,
                                f'{{{task.low_wcet}, {task.high_wcet}}}', "high" if task.criticality == t.TASK_PRIORITIES["high"] else "low"])

    return task_set


def generate_tasks(utilization: float, n: int, available_periods: list):
    task_set = []
    utilizations = []
    utilizations = generate_uunifastdiscard(
        u=utilization, n=n, filename='task_utilizations.csv')

    task_set = generate_tasksets(
        utilizations, available_periods)

    return task_set
