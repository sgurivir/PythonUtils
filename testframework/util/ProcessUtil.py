import os
import signal
import subprocess


def kill_pid(pid):
    """
    :param pid: Pid of process to be killed
    """
    try:
      os.kill(pid, signal.SIGKILL)
    except:
      pass


def kill_process(process_name):
    """
    :param process_name: Name of process to be killed
    """
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        if process_name in line:
            pid = int(line.split(None, 1)[0])
            kill_pid(pid)


def launch_process(full_path, kill_processes=[], args="", stdout=None, stderr=None):
     """
     :param full_path: Full path to the process to be launched
     :param kill_processes: Names of processes which should be killed before launching
     :param args: Arguments for launching the program
     :return: pid
     """
     for process_name in kill_processes:
         kill_process(process_name)
     p = subprocess.Popen(full_path + " " + args, shell=True, stdout=stdout, stderr=stderr)
     if p == 0:
         raise EnvironmentError()
     return p.pid


def sample_process(pid, out_file, duration=10, sample_interval=1):
    """
    :param pid: pid of process
    :param duration: Duration to sample
    :param sample_interval: Sampling interval
    :param file_output: where to write sample's output
    :return:
    """
    command = "sample"             + " " + \
              str(pid)             + " " + \
              str(duration)        + " " + \
              str(sample_interval) + " " + \
              " -f " + out_file    + " " + \
              " 2&> /dev/null"
    os.system(command)