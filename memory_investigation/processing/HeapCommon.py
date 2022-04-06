#!/usr/bin/python -u
# -*- coding: utf-8 -*-


class HeapObjectMetricCount:
    def __init__(self,
                 class_name,
                 object_type,
                 object_count,
                 total_bytes,
                 avg_size,
                 binary_name):
        self.class_name = class_name
        self.object_type = object_type
        self.object_count = object_count
        self.total_bytes = total_bytes
        self.avg_size = avg_size
        self.binary_name = binary_name

    @staticmethod
    def generate_object_count_from(line_in_heap_diff):
        """
        :param line_in_heap_diff:  text line in heap diff
        :return: An tuple of [object_type: HeapObjectAndCounts]
        """

        # Parse a string like
        #  17      55424    3260.2   _NSCallStackArray._frames (malloc[])              C       Foundation

        # Remove extra spaces
        line_in_heap_diff = " ".join(line_in_heap_diff.split())

        tokens = line_in_heap_diff.split(" ")
        if len(tokens) < 5:
            if not line_in_heap_diff.isspace():
                print("Ignoring line : {}".format(line_in_heap_diff))
            return None

        object_count = tokens[0]
        total_bytes = tokens[1]
        avg_size = tokens[2]
        binary_name = tokens[-1]
        object_type = tokens[-2]
        class_name = "".join(tokens[3:-2])

        h = HeapObjectMetricCount(class_name=class_name,
                                  object_type=object_type,
                                  object_count=object_count,
                                  total_bytes=total_bytes,
                                  avg_size=avg_size,
                                  binary_name=binary_name)

        return h


class HeapObjectAndCountGenerator:
    @staticmethod
    def generate_from_heap(path):
        """
        :param path: Path to heap file. A file which has Count of
        Object types, counts and sizes.

        This can be generated from either a heap_diff, or heap command (or) from
        a ExcResource file.

        :return: A dictionary of [Object_type: HeapObjectAndCounts]
        """
        object_counts = {}  # Dictionary of [String: HeapObjectAndCounts]

        with open(path, 'r') as f:
            # Keep reading until we find line with ==="
            line_underscored_before_metrics_found = False

            line = f.readline()
            while line:
                if "====" in line:
                    line_underscored_before_metrics_found = True
                    break
                line = f.readline()

            if line_underscored_before_metrics_found:
                line = f.readline()

                while line:
                    object_count = HeapObjectMetricCount.generate_object_count_from(line)
                    if object_count is not None:
                        if object_count.object_type is not None:
                            object_counts[object_count.class_name] = object_count

                            # print(f"{object_count.class_name} : {object_count}")

                    line = f.readline()
                    if line.isspace() or line == "\n":
                        break
            f.close()

        return object_counts
