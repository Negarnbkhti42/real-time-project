TASK_PRIORITIES = {"high": 1, "low": 2}


class Task:
    def __init__(self, name, utilization, period, criticality, low_wcet, high_wcet):
        self.utilization = utilization
        self.period = period
        self.name = name
        self.criticality = criticality
        self.high_wcet = high_wcet
        self.low_wcet = low_wcet if criticality == 1 else high_wcet
        self.relative_deadline = period
        self.executed_jobs = 0

    def __str__(self):
        return self.name

    def __lt__(self, other):
        return self.criticality < other.criticality


class TaskCopy(Task):
    def __init__(self, task, copy_number):
        super().__init__(
            task.name,
            task.utilization,
            task.period,
            task.criticality,
            task.low_wcet,
            task.high_wcet,
        )
        self.name = f"{task.name}_copy-{copy_number}"


class Job:
    def __init__(self, task):
        self.task = task
        self.number = task.executed_jobs
        self.deadline = (task.period * self.number) + task.relative_deadline
        self.remaining_exec_time = task.low_wcet

    def __lt__(self, other):
        if self.deadline == other.deadline:
            return self.task.criticality < other.task.criticality
        return self.deadline < other.deadline

    def __str__(self):
        job_string = f"{self.task.name}, Job_{self.number}"
        return job_string
