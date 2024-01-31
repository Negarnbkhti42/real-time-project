import random
import math
from models import task as t


class Core:
    def __init__(self, number, max_utilization):
        self.number = number
        self.max_utilization = max_utilization
        self.utilization = 0
        self.assigned_tasks = []
        self.is_in_overrun = False
        self.is_susceptible_to_overrun = False


class Processor:
    def __init__(self, num_of_cores, core_utilization):
        self.cores = []
        for i in range(num_of_cores):
            self.cores.append(Core(i + 1, core_utilization))

    def map_tasks(self, task_set, method):
        tasks = task_set.copy()
        tasks.sort(key=lambda task: task.utilization, reverse=True)
        assigned_tasks = []
        sorted_cores = self.cores.copy()
        for task in tasks:
            if method == "wfd":
                sorted_cores.sort(key=lambda core: core.utilization)

            selected_core = None

            for core in sorted_cores:
                if (task.number not in core.assigned_tasks) and (
                    core.utilization + task.utilization <= core.max_utilization
                ):
                    selected_core = core
                    break

            if selected_core is None:
                for core in sorted_cores:
                    if (task.number not in core.assigned_tasks) and (
                        core.utilization + task.utilization <= 1
                    ):
                        selected_core = core
                        break

            if selected_core is not None:
                selected_core.assigned_tasks.append(task.number)
                selected_core.utilization += task.utilization
                task.assigned_core = selected_core
            else:
                raise Exception(
                    "task is set is not schedulable with worst fit assignment"
                )

            assigned_tasks.append(task)

        return assigned_tasks

    def handle_overrun(self, active_jobs):
        for job in active_jobs:
            if job.task.criticality == t.TASK_PRIORITIES["high"]:
                task = job.task
                job.remaining_exec_time = (
                    task.high_wcet - task.low_wcet + job.remaining_exec_time
                )
                job.deadline = (task.period * job.number) + task.relative_deadline
            else:
                job.task.assigned_core = None

    def schedule_edf(self, task_set, duration, overrun_time, use_vd):
        current_time = 0
        schedule_timeline = []
        active_jobs = []
        QoS = []
        while duration > current_time:
            # find active_jobs
            for task in task_set:
                if current_time % task.period == 0:
                    is_core_in_overrun = False
                    if task.assigned_core is not None:
                        is_core_in_overrun = task.assigned_core.is_in_overrun

                    new_job = t.Job(
                        task,
                        is_core_in_overrun,
                        use_vd and is_core_in_overrun,
                    )
                    active_jobs.append(new_job)
                    task.executed_jobs += 1

            timestamp = []
            for core in self.cores:
                core_jobs = []
                selected_job = None

                # find acive jobs for a core, or migrating jobs
                for job in active_jobs:
                    if job.task.assigned_core == core:
                        core_jobs.append(job)

                if len(core_jobs) == 0:
                    # if core empty, execute a migrated job
                    migrated_jobs = [
                        job for job in active_jobs if job.task.assigned_core == None
                    ]
                    if len(migrated_jobs) > 0:
                        migrated_jobs.sort()
                        selected_job = migrated_jobs[0]
                else:
                    # schedule job with highest priority on core
                    core_jobs.sort()
                    selected_job = core_jobs[0]

                if selected_job is not None:
                    selected_task = selected_job.task

                    selected_job.remaining_exec_time = round(
                        selected_job.remaining_exec_time - 0.001, 3
                    )
                    if selected_job.remaining_exec_time == 0:
                        active_jobs.remove(selected_job)
                        if (
                            overrun_time is not None
                            and core.is_susceptible_to_overrun
                            and not core.is_in_overrun
                            and current_time >= overrun_time
                            and selected_task.criticality == t.TASK_PRIORITIES["high"]
                        ):
                            core.is_in_overrun = True
                            self.handle_overrun(active_jobs)
                        if (
                            selected_task.criticality == t.TASK_PRIORITIES["low"]
                            and selected_job.quality_of_service is None
                        ):
                            selected_job.quality_of_service = 1
                            QoS.append(selected_job.quality_of_service)

                    if (
                        selected_job.remaining_exec_time > 0
                        and current_time == selected_job.deadline
                    ):
                        if selected_task.criticality == t.TASK_PRIORITIES["high"]:
                            return schedule_timeline, sum(QoS) / len(QoS)
                        else:
                            selected_job.quality_of_service = 1 - (
                                selected_job.remaining_exec_time
                                / selected_task.low_wcet
                            )

                            QoS.append(selected_job.quality_of_service)

                    timestamp.append(
                        {
                            "task": selected_task,
                            "job": selected_job,
                            "core": core.number,
                            "overrun": core.is_in_overrun,
                        }
                    )
                else:
                    timestamp.append(
                        {
                            "task": None,
                            "job": None,
                            "core": core.number,
                            "overrun": core.is_in_overrun,
                        }
                    )

            schedule_timeline.append(timestamp)

            current_time = round(current_time + 0.001, 3)

        return schedule_timeline, sum(QoS) / len(QoS)

    def schedule_tasks(self, task_set, duration, overrun_rate, scheduling_method):
        for core in self.cores:
            # get tasks assigned to this core
            core_tasks = [task for task in task_set if task.assigned_core == core]

            # calculate virtual deadline for tasks in this core
            sum_of_high_crit_util = sum(
                [
                    task.low_wcet / task.period
                    for task in core_tasks
                    if task.criticality == t.TASK_PRIORITIES["high"]
                ]
            )
            sum_of_high_crit_high_wcet_util = sum(
                [
                    task.utilization
                    for task in core_tasks
                    if task.criticality == t.TASK_PRIORITIES["high"]
                ]
            )
            sum_of_low_crit_util = sum(
                [
                    task.utilization
                    for task in core_tasks
                    if task.criticality == t.TASK_PRIORITIES["low"]
                ]
            )
            virtual_deadline_multiplier = sum_of_high_crit_util / (
                1 - sum_of_low_crit_util
            )

            # test schedulability using gained x
            if (
                (virtual_deadline_multiplier * sum_of_low_crit_util)
                + sum_of_high_crit_high_wcet_util
            ) > 1:
                raise Exception("not schedulable")

            # apply virtual deadline
            for task in core_tasks:
                if task.criticality == t.TASK_PRIORITIES["high"]:
                    task.virtual_deadline = task.period * virtual_deadline_multiplier

        n = math.floor(overrun_rate * len(self.cores))
        susceptible_cores = random.sample(self.cores, n)
        for core in susceptible_cores:
            core.is_susceptible_to_overrun = True

        return self.schedule_edf(
            task_set,
            duration,
            None if overrun_rate == 0 else duration / 2,
            scheduling_method == "edf-vd",
        )
