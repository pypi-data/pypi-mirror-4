import os
import socket
import time
from sittercommon import address
from tasksitter.stats_collector import StatsCollector


class MachineStats(StatsCollector):

    hostname_expire = 600
    hostname_create = None

    @classmethod
    def get_hostname(cls):
        now = time.time()
        cache = True
        if (cls.hostname_create is None or 
                now - cls.hostname_create >= cls.hostname_expire):
            cls.hostname_create = now
            cache = False
        return address.get_external_address(True, cache=cache)

    def get_live_data(self):
        data = {}
        for task_name, task in self.harness.tasks.items():
            running = bool(task.is_running())
            data["%s-running" % task.name] = running
            if not running:
                data["%s-start" % task.name] = \
                    "<a href='http://%s:%s/start_task?task_name=%s'>start</a>" % (
                    self.get_hostname(),
                    self.harness.http_monitor.port,
                    task.name)
                data["%s-remove" % task.name] = \
                    "<a href='http://%s:%s/remove_task?task_name=%s'>remove</a>" % (
                    self.hostname,
                    self.harness.http_monitor.port,
                    task.name)
            else:
                data["%s-stop" % task.name] = \
                    "<a href='http://%s:%s/stop_task?task_name=%s'>stop</a>" % (
                    self.hostname,
                    self.harness.http_monitor.port,
                    task.name)

                data["%s-reboot" % task.name] = \
                    "<a href='http://%s:%s/restart_task?task_name=%s'>restart</a>" % (
                    self.hostname,
                    self.harness.http_monitor.port,
                    task.name)

                location = "http://%s:%s" % (
                    self.hostname,
                    task.http_monitoring_port)
                data["%s-monitoring" % task.name] = "<a href='%s'>%s</a>" % (location,
                                                                           location)

        load = os.getloadavg()
        data['load_one_min'] = load[0]
        data['load_five_min'] = load[1]
        data['load_fifteen_min'] = load[2]

        return data

    def get_metadata(self):
        data = {}
        data['hostname'] = self.get_hostname()
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
