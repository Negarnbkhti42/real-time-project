from models import task as t


class Core:
    def __init__(self, number, max_utilization):
        self.number = number
        self.max_utilization = max_utilization
        self.utilization = 0
        self.assigned_tasks = []


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

    def handle_overrun(self, task_set, migrated_jobs, migrated_tasks):
        for indx, task in enumerate(task_set):
            if task.criticality == t.TASK_PRORITIES["low"]:
                task_set.pop(indx)
                migrated_tasks.append(task)

        for job in active_jobs:
            if job.task.criticality == t.TASK_PRORITIES["low"]:
                migrated_job.append(t.MigratedJob(job, current_time))

    def schedule_core(
        self, task_set, duration, migrated_jobs, migrated_tasks, overrun_time
    ):
        current_time = 0
        schedule_timeline = []
        active_jobs = []
        is_in_overrun = False

        while current_time < duration:
            for task in task_set:
                # find active jobs
                if current_time % task.period == 0:
                    new_job = t.Job(task, is_in_overrun)
                    active_jobs.append(new_job)
                    task.executed_jobs += 1

                # migrate jobs at correct time
                for migrated_job in migrated_jobs:
                    if migrated_job.migration_time == current_time:
                        active_job.append(migrated_job)
                        task_set.append(migrated_job.task)

            # schedule task with highest priority on core
            if len(active_jobs) > 0:
                active_jobs.sort()
                selected_job = active_jobs[0]
                selected_task = selected_job.task
                selected_job.remaining_exec_time -= 1

                task_will_overrun = False
                if (
                    (not is_in_overrun)
                    and current_time >= overrun_time
                    and selected_task.criticality == t.TASK_PRIORITIES["high"]
                ):
                    task_will_overrun = True

                if (
                    len(schedule_timeline) > 0
                    and schedule_timeline[-1]["task"] == selected_task
                ):
                    schedule_timeline[-1]["duration"][1] += 1
                else:
                    schedule_timeline.append(
                        {
                            "task": selected_task,
                            "job": selected_job,
                            "duration": [current_time, current_time + 1],
                        }
                    )

                if selected_job.remaining_exec_time == 0:
                    if task_will_overrun:
                        is_in_overrun = True
                        self.handle_overrun(task_set, migrated_jobs, migrated_tasks)
                        selected_job.remaining_exec_time = (
                            selected_task.high_wcet - selected_task.low_wcet
                        )
                    else:
                        active_jobs.pop(0)
                elif current_time >= selected_job.deadline:
                    raise Exception(
                        f"deadline for job {selected_job.number} of {selected_job.task.name} missed!"
                    )
            else:
                schedule_timeline.append({"task": None})

            current_time += 0.001

        return schedule_timeline

    def schedule_tasks(self, task_set, duration):
        tasks_separated_by_core = []
        core_schedules = []
        migrated_jobs = []
        migrated_tasks = []
        for core in self.cores:
            # get tasks assigned to this core
            core_tasks = [task for task in task_set if task.assigned_core == core]
            tasks_separated_by_core.append(core_tasks)

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

            core_schedules.append(
                self.schedule_core(
                    core_tasks, duration, migrated_jobs, migrated_tasks, duration / 2
                )
            )

        return core_schedules
