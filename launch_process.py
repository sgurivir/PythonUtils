import os
import subprocess

class ProcessUtil:
    @staticmethod
    def launch_process(full_path, args="", kill_processes=[], stdout=None, stderr=None, env=None):
        """
        :param full_path: Full path to the process to be launched
        :param kill_processes: Names of processes which should be killed before launching.
        This arguments helps in cleaning up stale processes before launching a test program.
        :param args: Arguments for launching the program
        :return: pid
        """
        for process_name in kill_processes:
            ProcessUtil.kill_process(process_name)

        process = subprocess.Popen([full_path , args], shell=True, stdout=stdout, stderr=stderr, env=env)
        if process == 0:
            raise EnvironmentError()
        return process.pid

ProcessUtil.launch_process("/Applications/FusionX.app")
