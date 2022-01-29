import pandas
import re

elements = ["word1 word2 word3", "word1 word3 word4", "word1 word5 word2"]

words_count = {}
each_word = []


def words_counter(some_list):
    for element in some_list:
        for word in re.split(" ", element):
            each_word.append(word)
    words_count.update(pandas.value_counts(each_word))


words_counter(elements)

print(words_count)
