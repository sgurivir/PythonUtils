import glob
import numpy as np
import os


class FileSystemUtil:
    @staticmethod
    def sorted_files_in_dir(path, extension):
        """
        returns a list of files found in provided directory, with the given extension
        :param(path): directory to search memgraph files
        :param(extension): File extension
        :return: Paths to files, sorted in canonical order
        """
        files = glob.glob(path + f'/*.{extension}', recursive=False)
        files.sort()
        return files

    @staticmethod
    def get_paths_to_memgraphs(file_or_directory):
        """
        Enumerate memgraphs in a directory
        """
        if not os.path.exists(file_or_directory):
            raise Exception(f"Path provided does not exist : {file_or_directory}")

        if os.path.isfile(file_or_directory):
            return [file_or_directory]

        if os.path.isdir(file_or_directory):
            memgraphs = FileSystemUtil.sorted_files_in_dir(path=file_or_directory,
                                                           extension="memgraph")

            if len(memgraphs) == 0:
                raise Exception(f"No memgraphs found in directory provided : {file_or_directory}")

            return memgraphs

        return []

    @staticmethod
    def pick_two_memgraphs(paths_to_memgraphs, skip_first_if_more_than_two=False):
        """
        If we have more than two memgraphs, pick two which would best fit for analysis.

        :param(paths_to_memgraphs): Paths to memgraphs
        :param(skip_first_if_more_than_two) : Should we skip first memgraph, if there are more than two
        """
        num_memgraphs = len(paths_to_memgraphs)

        first_index = 0
        if skip_first_if_more_than_two is True and num_memgraphs > 2:
            first_index = 1

        return paths_to_memgraphs[first_index], paths_to_memgraphs[-1]

    @staticmethod
    def pick_memgraphs_for_analysis(memgraphs_,
                                    max_count,
                                    skip_first_if_more_than_two=True):
        """
        If there are more than max memgraphs to process, pick memgraphs for analysis
        """
        print("\n======= Picking Memgraphs for analysis ======= ")
        num_memgraphs = len(memgraphs_)

        # Override include_first, if only two memgraphs are available
        if num_memgraphs <= 2:
            skip_first_if_more_than_two = False

        # remove first memgraph, if needed
        if skip_first_if_more_than_two:
            memgraphs_ = memgraphs_[1:]

        def uniform_dist(min, max, count):
            l_ = np.random.randint(min, max, count).tolist()
            return list(sorted(set(l_)))

        # Pick First
        included_memgraphs = [memgraphs_[0]]

        # Pick uniformly distributed memgraphs, in between
        if num_memgraphs > 3:
            for index in uniform_dist(1, len(memgraphs_)-2, max_count-2):
                included_memgraphs.append(memgraphs_[index])
        elif num_memgraphs == 3:
            included_memgraphs.append(memgraphs_[1])

        # Pick Last
        included_memgraphs.append(memgraphs_[-1])

        print("\t\n\t".join(included_memgraphs))

        return included_memgraphs

