import glob
import os
import pickle
import random


class Tile:
    def __init__(self, value, is_found):
        self.value = value
        self.is_found = is_found

    def dump(self):
        print("{}, {}".format(self.value, self.is_found))


class BoardModel:
    SIZE_OF_BOARD = 9
    MAX_WORD_LENGTH = 5
    NUM_WORDS = 6
    MAX_COMMON_LETTERS = 3
    MIN_COMMON_LETTERS = 1

    def __init__(self):
        rows, cols = (BoardModel.SIZE_OF_BOARD, BoardModel.SIZE_OF_BOARD)
        self.tiles = [0] * cols * rows
        self.size = BoardModel.SIZE_OF_BOARD
        self.num_words = BoardModel.NUM_WORDS

        self.start_index_for_row = {}
        self.length_of_word_for_row = {}
        self.start_index_for_column = {}
        self.length_of_word_for_column = {}

    def dump(self):
        print("=====" * self.size)
        output = ""
        for idx, row in enumerate(self.tiles):
            output = output + " | {} ".format(row)
            if (idx+1) % BoardModel.SIZE_OF_BOARD == 0:
                output += "\n"
        print(output[:-1])
        print("=====" * self.size)

    def sum_beg_end(self, b, e):
        sum_ = 0
        for c in range(b, e+1):
            sum_ += self.tiles[c]

        return sum_

    def find_boxes_to_fill(self):
        find_row_or_column = False  # true for row, false for column
        rows_filled = []
        columns_filled = []

        found_word_in_this_iteration = False
        while (len(self.start_index_for_row.keys()) + len(self.start_index_for_column.keys())) < self.num_words:
            length_of_word = random.randint(3, BoardModel.MAX_WORD_LENGTH)

            if found_word_in_this_iteration:
                find_row_or_column = not find_row_or_column  # find row and column alternately

                # Override if we found enough rows or columns
                if len(self.start_index_for_row.keys()) == self.num_words/2:
                    find_row_or_column = False
                elif len(self.start_index_for_column.keys()) == self.num_words/2:
                    find_row_or_column = True

            if find_row_or_column is True:
                for r in range(0, self.size):
                    if r % 2 != 0:
                        continue

                    if self.start_index_for_row.keys().__contains__(r):
                        continue

                    beg = r * self.size
                    end = (r+1) * self.size - 1

                    if self.sum_beg_end(beg, end) >= BoardModel.MAX_COMMON_LETTERS:
                        continue
                    c = random.randint(1, self.size - length_of_word -2)

                    # words can only start in even rows
                    if c % 2 == 1:
                        c = c - 1

                    self.tiles[beg + c: beg + c + length_of_word] = [1] * length_of_word
                    found_word_in_this_iteration = True
                    rows_filled.append(r)
                    self.start_index_for_row[r] = c
                    self.length_of_word_for_row[r] = length_of_word
                    break

            else:
                starting_column_to_search = random.randint(0, self.size-1)
                for c_ in range(starting_column_to_search, self.size + starting_column_to_search):
                    # words can only start in even columns
                    if c_ % 2 == 1:
                        c_ = c_ + 1
                    c = c_ % self.size

                    if self.start_index_for_column.keys().__contains__(c):
                        continue

                    r = random.randint(0, self.size - length_of_word)
                    sum = 0
                    for k in range(r, length_of_word):
                        sum = sum + self.tiles[k*self.size + c]
                    #print("Sum: {} for c: {} and r:{}".format(sum, c, r))

                    if sum <= BoardModel.MAX_COMMON_LETTERS:
                        for k in range(0, length_of_word):
                            self.tiles[(r+k) * self.size + c] = 1
                        found_word_in_this_iteration = True

                        columns_filled.append(c)
                        self.start_index_for_column[c] = r
                        self.length_of_word_for_column[c] = length_of_word
                        break


def load_thesaurus(path):
    with open(thesaurus_path, 'rb') as t:
        all_words = pickle.load(t)
        words = {}
        for word_length in range(3, BoardModel.MAX_WORD_LENGTH + 1):
            words[word_length] = list(filter(lambda w: len(w) == word_length, all_words))
        return words


if __name__ == '__main__':
    board = BoardModel()
    board.find_boxes_to_fill()
    board.dump()

    thesaurus_path = "/Users/sgurivireddy/my_src/PythonUtils/wordScrabble/output/Board_Dictionary"
    words = load_thesaurus(thesaurus_path)

