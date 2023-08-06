import os
from tasksitter.stats_collector import StatsCollector


class MachineStats(StatsCollector):

    def get_live_data(self):
        self.update_hostname()
        data = {}
        for task_name, task in self.harness.tasks.items():
            running = bool(task.is_running())
            data["%s-running" % task.name] = running
            if not running:
                data["%s-start" % task.name] = \
                    "<a href='http://%s:%s/start_task?task_name=%s'>start</a>" % (
                    self.hostname_external,
                    self.harness.http_monitor.port,
                    task.name)
                data["%s-remove" % task.name] = \
                    "<a href='http://%s:%s/remove_task?task_name=%s'>remove</a>" % (
                    self.hostname_external,
                    self.harness.http_monitor.port,
                    task.name)
            else:
                data["%s-stop" % task.name] = \
                    "<a href='http://%s:%s/stop_task?task_name=%s'>stop</a>" % (
                    self.hostname_external,
                    self.harness.http_monitor.port,
                    task.name)

                data["%s-reboot" % task.name] = \
                    "<a href='http://%s:%s/restart_task?task_name=%s'>restart</a>" % (
                    self.hostname_external,
                    self.harness.http_monitor.port,
                    task.name)

                location = "http://%s:%s" % (
                    self.hostname_external,
                    task.http_monitoring_port)
                data["%s-monitoring" % task.name] = "<a href='%s'>%s</a>" % (location,
                                                                           location)

        load = os.getloadavg()
        data['load_one_min'] = load[0]
        data['load_five_min'] = load[1]
        data['load_fifteen_min'] = load[2]

        return data

    def get_metadata(self):
        self.update_hostname()
        data = {}
        data['hostname'] = self.hostname
        data['hostname_external'] = self.hostname_external
        data['machinesitter_pid'] = os.getpid()
        data['launch_location'] = self.harness.launch_location
        data['log_location'] = self.harness.log_location
        data['task_sitter_starting_port'] = self.harness.task_sitter_starting_port
        data['machine_sitter_starting_port'] = self.harness.machine_sitter_starting_port
        data['task_definition_file'] = self.harness.task_definition_file
        for task_name, task in self.harness.tasks.items():
            data["%s-name" % task.name] = task.name
            data["%s-command" % task.name] = task.command

        return data
