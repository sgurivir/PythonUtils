
from dateutil import parser
import subprocess


class MemgraphUtil:

    @staticmethod
    def pid_for(path, daemon="locationd"):
        """
        Looks up PID of daemon inside memgraph
        :param path: Path to memgraph
        :param daemon: process name for daemon
        :return: a list of daemon pids and a dictionary of date to footprint
        """

        # The line producted by footprint command is like below. Extract footprint from the line
        # daemon [76] (memgraph): 64-bit\tFootprint: 71 MB (16384 bytes per page)\n'
        def pid_from(line):
            opening_bracket_index = line.index('[')
            closing_bracket_index = line.index(']')
            return line[opening_bracket_index + 1:closing_bracket_index]

        with subprocess.Popen(["footprint", path],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as p_1:
            with subprocess.Popen(['grep', daemon],
                                  stdin=p_1.stdout,
                                  stdout=subprocess.PIPE) as p_2:
                p_1.stdout.close()
                stdout, _ = p_2.communicate()
                stdout = stdout.decode("utf-8")

                pid = pid_from(stdout)
                return pid

    @staticmethod
    def footprint_for(path):
        """
        returns footprint from memgraph
        :param path: Path to memgraph
        :return: footprint
        """
        p1 = subprocess.Popen(["footprint", path], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "phys_footprint: "], stdin=p1.stdout, stdout=subprocess.PIPE)
        footprint = p2.communicate()[0].decode("utf-8")

        footprint = footprint.replace("phys_footprint: ", "")
        footprint = footprint.replace("\n", "")
        footprint = footprint.replace("\t", "")
        return footprint

    @staticmethod
    def timestamp_for(path):
        """
        returns Date When memgraph was taken
        :param path: Path to memgraph
        :return: DateTime object when memgraph was collected
        """
        with subprocess.Popen(["leaks", "--processInfo", path],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as p_1:
            with subprocess.Popen(['grep', "Date/Time"],
                                  stdin=p_1.stdout,
                                  stdout=subprocess.PIPE) as p_2:
                p_1.stdout.close()
                stdout, _ = p_2.communicate()
                stdout = stdout.decode("utf-8")

                stdout = stdout.replace("Date/Time:  ", "")
                stdout = stdout.replace("\n", "")
                return parser.parse(stdout)

    @staticmethod
    def fragmentation_stats_for(path, zone_name="MallocStackLoggingLiteZone"):
        cmd = f'vmmap --summary {path} | grep -A 7 FRAG | grep -v "FRAG" | grep -v "=="  | grep {zone_name}'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = process.communicate()[0].decode("utf-8")

        # Find word with percentage
        words = output.split(" ")

        # Return first word which has %
        def contains_percent(word):
            return word.find("%") != -1
        fragmentation = next(filter(contains_percent, words), None)
        bytes_allocated = words[6]

        return {"fragmentation": fragmentation,
                "bytes_allocated": bytes_allocated}

    @staticmethod
    def generate_heap_diff(paths_to_memgraphs, out_dir):
        """
        Generate a memtrend from a list of memgraphs
        :param paths_to_memgraphs: Input memgraphs
        :param out_dir: Output directory
        :return: None
        """
        print("\n\n=====Generating heap_diff ====")

        out_path = os.path.join(out_dir, "heap_diff.txt")
        command = "heap -s --guessNonObjects --sumObjectFields {} --diffFrom {} > {}".format(
            paths_to_memgraphs[-1],
            paths_to_memgraphs[0],
            out_path)

        print(f"Generating Heap diff at {out_path} ....\n")
        print(f"\t Running: {command}")
        os.system(f"{command} > {out_path}")

    @staticmethod
    def generate_malloc_history(path, out_dir):
        """
        Run malloc_history on memgraphs
        :param path: Input memgraph
        :param out_dir: Output directory
        :return: None
        """
        out_path = path
        out_path = path.replace(".memgraph", ".txt")

        consolidated_out_path = out_path.replace("memgraph_", "malloc_history_consolidated_")
        command = f"malloc_history -callTree -consolidateAllBySymbol {memgraph} > {consolidated_out_path}"
        print(command)
        os.system(f"{command}")

        # Generate malloc_history with fullStacks for last memgraph
        out_path = os.path.join(out_dir, "malloc_history_fullStacks.txt")
        command = f"malloc_history --fullStacks -allBySize  {paths_to_memgraphs[-1]} > {out_path}"
        print(command)
        os.system(f"{command}")

    @staticmethod
    def has_os_transactions(path):
        """
        Inspects memgraph where there are objects of OS_os_transactions
        :param path: Input memgraph
        :return: True or False
        """
        with subprocess.Popen(["heap", "-q", "-s", "--guessNonObjects", "--addresses='.*_os_*transaction'", path],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as p_1:
            with subprocess.Popen(['wc', '-l'],
                                  stdin=p_1.stdout,
                                  stdout=subprocess.PIPE) as p_2:
                p_1.stdout.close()

                stdout, _ = p_2.communicate()
                os_transaction_count = int(stdout.decode("utf-8"))
                p_2.stdout.close()

        return os_transaction_count > 0


    @staticmethod
    def validate_is_generated_for_daemon(paths, daemon_name):
        """
        Validates memgraph was generated for provided daemon

        :param paths: Path to memgraphs
        :param daemon_name: Name of daemon
        :return: None
        """
        if not isinstance(paths, list):
            paths = [paths]

        for path in paths:
            with subprocess.Popen(["footprint", path],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as p_1:
                with subprocess.Popen(['grep', daemon_name],
                                      stdin=p_1.stdout,
                                      stdout=subprocess.PIPE) as p_2:
                    p_1.stdout.close()

                    p2_stdout, _ = p_2.communicate()
                    p2_stdout = p2_stdout.decode("utf-8")

                    # Validate the memgraph was generated for this daemon
                    if p2_stdout == "":
                        return False

        return True

    @staticmethod
    def validate_pid_has_not_changed(paths, daemon_name):
        """
        Validates daemon has not crashed and restarted during the data collection

        :param paths: Path to memgraphs
        :param daemon_name: Name of daemon
        :return: None
        """
        print("\n\n=====Validating Process has not crashed while collecting memgraphs ====")
        if not isinstance(paths, list):
            paths = [paths]

        pids = [MemgraphUtil.pid_for(path, daemon_name) for path in paths]

        # Check if only one unique pid exists
        if len(set(pids)) != 1:
            raise Exception(f"Pid has changed for {daemon_name} in provided memgraphs")


