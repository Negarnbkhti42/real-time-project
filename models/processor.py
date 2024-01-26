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

            if method == 'wfd':
                sorted_cores.sort(
                    key=lambda core: core.utilization)

            selected_core = None

            for core in sorted_cores:
                if core.utilization + task.utilization <= core.max_utilization:
                    selected_core = core
                    break

            if selected_core is None:
                for core in sorted_cores:
                    if core.utilization + task.utilization <= 1:
                        selected_core = core
                        break

            if selected_core is not None:
                selected_core.utilization += task.utilization
                task.assigned_core = selected_core
            else:
                raise Exception(
                    "task is set is not schedulable with worst fit assignment")

            assigned_tasks.append(task)

        return assigned_tasks

    def schedule_core(self, task_set, duration):
        current_time = 0
        schedule_timeline = []
        active_jobs = []

        while current_time < duration:

            for task in task_set:
                if current_time % task.period == 0:
                    new_job = t.Job(task)
                    active_jobs.append(new_job)
                    task.executed_jobs += 1

            if len(active_jobs) > 0:
                active_jobs.sort()
                selected_job = active_jobs[0]
                selected_job.remaining_exec_time -= 1
                selected_task = selected_job.task
                if len(schedule_timeline) > 0 and schedule_timeline[-1]["task"] == selected_task:
                    schedule_timeline[-1]["duration"][1] += 1
                else:
                    schedule_timeline.append({"task": selected_task, "job": selected_job, "duration": [
                                             current_time, current_time + 1]})

                if selected_job.remaining_exec_time == 0:
                    active_jobs.pop(0)
                elif current_time == selected_job.deadline:
                    raise Exception(
                        f'deadline for job {selected_job.number} of {selected_job.task.name} missed!')
            else:
                schedule_timeline.append({"task": None})

            current_time += 1

        return schedule_timeline

    def schedule_tasks(self, task_set, duration):
        core_schedules = []
        for core in self.cores:
            core_tasks = [
                task for task in task_set if task.assigned_core == core]
            core_schedules.append(self.schedule_core(core_tasks, duration))

        return core_schedules
