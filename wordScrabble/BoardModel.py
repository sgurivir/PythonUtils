import glob
import os
import random


class Tile:
    def __init__(self, value, is_found):
        self.value = value
        self.is_found = is_found

    def dump(self):
        print("{}, {}".format(self.value, self.is_found))


class BoardModel:
    SIZE_OF_BOARD = 10
    MAX_WORD_LENGTH = 5
    NUM_WORDS = 8
    MAX_COMMON_LETTERS = 2

    def __init__(self):
        rows, cols = (BoardModel.SIZE_OF_BOARD, BoardModel.SIZE_OF_BOARD)
        self.tiles = [0] * cols * rows
        self.size = BoardModel.SIZE_OF_BOARD
        self.num_words = BoardModel.NUM_WORDS

    def dump(self):
        print("====" * self.size)
        output = ""
        for idx, row in enumerate(self.tiles):
            output = output + " | {}".format(row)
            if (idx+1) % BoardModel.SIZE_OF_BOARD == 0:
                output += "\n"
        print(output)
        print("====" * self.size)

    def sum_beg_end(self, b, e):
        sum_ = 0
        for c in range(b, e+1):
            sum_ += self.tiles[c]

        return sum_

    def find_boxes_to_fill(self):

        find_row_or_column = True  # true for row, false for column
        rows_filled = []
        columns_filled = []
        start_index_for_row = {}
        start_index_for_column = {}

        found = False
        for x in range(self.num_words):
            length_of_word = random.randint(3, BoardModel.MAX_WORD_LENGTH)
            board.dump()

            if found:
                find_row_or_column = not find_row_or_column  # find row and column alternately

            if find_row_or_column is True:
                for r in range(1, self.size -1):
                    if start_index_for_row.keys().__contains__(r) or \
                        start_index_for_row.keys().__contains__(r+1) or \
                        start_index_for_row.keys().__contains__(r-1):
                        continue

                    beg = r * self.size
                    end = (r+1) * self.size - 1

                    if self.sum_beg_end(beg, end) < BoardModel.MAX_COMMON_LETTERS:
                        c = random.randint(1, self.size - length_of_word -1)
                        self.tiles[beg + c: beg + c + length_of_word] = [1] * length_of_word
                        print("FOUND  ROW - {} {}".format(r, c))
                        found = True
                        rows_filled.append(r)
                        start_index_for_row[r] = c
                        break
                    if found:
                        break

                if found:
                    continue
            else:
                starting_column_to_search = random.randint(1, self.size-1)
                for c_ in range(starting_column_to_search, self.size + starting_column_to_search-1):
                    c = c_ % self.size
                    if start_index_for_column.keys().__contains__(c) or \
                        start_index_for_column.keys().__contains__(c+1) or \
                        start_index_for_column.keys().__contains__(c-1):
                        continue

                    sum = 0
                    for r in range(0, self.size - length_of_word):
                        sum = sum + self.tiles[r*self.size + c]

                    if sum <= BoardModel.MAX_COMMON_LETTERS:
                        for r in range(r, r + length_of_word):
                            self.tiles[r * self.size + c] = 1
                        print("FOUND COLUMN {}".format(c))
                        found = True

                        columns_filled.append(c)
                        start_index_for_column[c] = r
                        break
                if found:
                    continue

            print("NOT FOUND")

        print(start_index_for_row)
        print(start_index_for_column)


if __name__ == '__main__':
    board = BoardModel()
    board.find_boxes_to_fill()
    board.dump()
