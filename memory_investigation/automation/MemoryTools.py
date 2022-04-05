
import argparse
import glob
import os
import subprocess
import sys

from MemgraphUtil import MemgraphUtil


class MemoryTools:
    @staticmethod
    def generate_memtrend(paths_to_memgraphs, out_path):
        """
        Generate a memtrend from a list of memgraphs
        :param paths: Input memgraphs
        :param out_path: Output to memtrend
        :return: None
        """
        print("\n\n=====Generating memtrend ====")

        memgraphs_concatenated = " ".join(paths_to_memgraphs)
        command = f"memtrend  -guessNonObjects  -showSizes {memgraphs_concatenated}"

        print(f"Generating memtrend at {out_path} ....\n")
        print(f"\t Running: {command}")
        os.system(f"{command} > {out_path}")

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
    def generate_malloc_history(paths_to_memgraphs, out_dir):
        """
        Run malloc_history on memgraphs
        :param paths: Input memgraphs
        :param out_dir: Output directory
        :return: None
        """
        print("\n\n=====Generating malloc_history for memgraphs====")

        for memgraph in paths_to_memgraphs:
            out_path = memgraph
            out_path = out_path.replace(".memgraph", ".txt")

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
    def generate_flamegraph(paths_to_memgraphs, out_path):
        """
        Generate a flamegraph from a list of memgraphs
        :param paths_to_memgraphs: Input memgraphs
        :param out_path: Output to flamegraph
        :return: None
        """
        print("\n\n======Generating flamegraph=====")
        paths_to_memgraphs.sort()

        memgraphs_concatenated = " ".join(paths_to_memgraphs)
        command = f"ardiff callstacks  -o {out_path}  --flame  {memgraphs_concatenated}"

        print(f"Generating flamegraph at {out_path}")
        print(f"Running: {command}")
        os.system(f"{command}")

    @staticmethod
    def generate_fragmentation_stats(paths_to_memgraphs, out_path):
        """
        Calculate fragmentation statistics for each memgraph and creates a fragmentation report
        :param paths_to_memgraphs: Input memgraphs
        :param out_path: Output path
        :return: None
        """
        print("============ Fragmentation analysis ==========================")
        with open(out_path, "w") as f_:
            for memgraph in paths_to_memgraphs:
                timestamp = MemgraphUtil.timestamp_for(path=memgraph)
                fragmentation_stats = MemgraphUtil.fragmentation_stats_for(path=memgraph)
                f_.write("\t {} : {}, {} \n".format(timestamp,
                                                    fragmentation_stats["fragmentation"],
                                                    fragmentation_stats["bytes_allocated"]))
            f_.close()

    @staticmethod
    def find_memgraphs_with_zero_transactions(paths_to_memgraphs, out_csv):
        """
        Inspects memgraphs where there are zero objects of OS_os_transactions and
        generates CSV of path_to_memgraph, footprint
        :param paths_to_memgraphs: Input memgraphs
        :param out_csv: Path to Output CSV
        :return: None
        """
        print("\n\n=====Identifying memgraphs with zero transactions====")

        with open(out_csv, "w") as f_:
            for memgraph in paths_to_memgraphs:
                if not MemgraphUtil.has_os_transactions(memgraph):
                    footprint = MemgraphUtil.footprint_for(memgraph)
                    timestamp = MemgraphUtil.timestamp_for(memgraph)
                    f_.write(f"{memgraph}, {timestamp}, {footprint}")
            f_.close()
