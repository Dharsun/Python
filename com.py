def find_unique_words(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        words1 = set(f1.read().split())
        words2 = set(f2.read().split())

    unique_words = words1 - words2
    return unique_words

file1_path = 'pass.txt'
file2_path = 'fail.txt'

result = find_unique_words(file1_path, file2_path)

print("Unique words in the first file:", result)
