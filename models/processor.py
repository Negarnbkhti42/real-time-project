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
                    key=lambda core: core.utilization, reverse=True)

            selected_core = None

            for core in sorted_cores:
                if core.utilization + task.utilization <= core.max_utilization:
                    selected_core = core

            if selected_core is None:
                for core in sorted_cores:
                    if core.utilization + task.utilization <= 1:
                        selected_core = core

            if selected_core != None:
                selected_core.utilization += task.utilization
                task.assigned_core = selected_core
            else:
                print("not schedulable")
                return assigned_tasks
                # raise Exception(
                #     "task is set is not schedulable with worst fit assignment")

            assigned_tasks.append(task)

        return assigned_tasks
