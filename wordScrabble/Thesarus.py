import glob
import os
import pickle
import random
from textblob import TextBlob

class ThesarusGenerator:
    def __init__(self, directory, out_directory):
        self.directory = directory
        self.out_directory = out_directory

        os.makedirs(self.out_directory, exist_ok=True)

    def scan_file(self,
                  path_to_file,
                  min_length,
                  max_length,
                  min_frequency,
                  max_frequency):
        counts = {}

        with open(path_to_file, 'r') as file:
            # reading each line
            for line in file:
                for word in line.split():
                    if not word.isalpha() or len(word) < min_length or len(word) > max_length:
                        continue
                    word = word.lower()
                    if counts.keys().__contains__(word):
                        counts[word] += 1
                    else:
                        counts[word] = 1

        keys_to_pop = []
        for word in counts.keys():
            if counts[word] < min_frequency or counts[word] > max_frequency:
                keys_to_pop.append(word)

        for key in keys_to_pop:
            counts.pop(key)

        return counts

    def scan_and_generate(self,
                          min_length,
                          max_length,
                          min_frequency,
                          max_frequency):
        # Scan each file and get frequencies of words
        counts_per_file = []
        discarded_words = []
        for file in os.listdir(self.directory):
            if file.endswith(".txt"):
                path = os.path.join(self.directory, file)
                counts = self.scan_file(path, min_length, max_length, min_frequency, max_frequency)
                counts_per_file.append(counts)
                # print("\n\n=========  {} : {}  =========".format(file, len(counts.keys())))
                # print(counts)

        # Find how many unique files each words shows up
        keys_dictionary = {}
        for counts in counts_per_file:
            for word in counts.keys():
                if keys_dictionary.keys().__contains__(word):
                    keys_dictionary[word] += 1
                else:
                    keys_dictionary[word] = 1

        # Remove words which only show up in one file
        for key in keys_dictionary:
            if keys_dictionary[key] <= 2:
                discarded_words.append(key)
        for discard_word in discarded_words:
            keys_dictionary.pop(discard_word)


        #print("\n==========Final Dictionary ===========")
        #for word in keys_dictionary.keys():
        #    print("{}, ".format(TextBlob(word).correct()))
        #print(len(keys_dictionary.keys()))
        # print("========+XXXXXXXX Discarded=========")
        # print(discarded_words)
        # print(len(discarded_words))

        # Spell correction
        corrected_words = map(lambda x: str(TextBlob(x).correct()), keys_dictionary.keys())
        return list(corrected_words)


if __name__ == '__main__':
    thesarus = ThesarusGenerator(directory="/Users/sgurivireddy/my_src/PythonUtils/wordScrabble/input/",
                                 out_directory="/Users/sgurivireddy/my_src/PythonUtils/wordScrabble/output")
    words = thesarus.scan_and_generate(min_length=3,
                                       max_length=7,
                                       min_frequency=2,
                                       max_frequency=40)

    out_file_path = "/Users/sgurivireddy/my_src/PythonUtils/wordScrabble/output/Board_Dictionary"
    with open(out_file_path, 'wb') as t_:
        pickle.dump(words, t_)

    words = []
    with open(out_file_path, 'rb') as temp:
        words = pickle.load(temp)
        print(words)
    print("Found {} words".format(len(words)))

