import nltk
import sys

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    import os 

    files = dict()

    for filename in os.listdir(directory):
        if not filename.endswith(".txt"):
            continue

        with open(os.path.join(directory, filename), encoding='utf-8') as file:
            files[filename] = file.read()

    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    import string
    try:
        nltk.corpus.stopwords.words('english')
    except LookupError:
        nltk.download('stopwords')

    words = []
    for word in nltk.tokenize.word_tokenize(document.lower()):
        if word in nltk.corpus.stopwords.words("english"):
            continue
        alpha = False
        for letter in word:
            if letter not in string.punctuation:
                alpha = True
                continue
        if alpha:
            words.append(word)

    return words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    import math

    num_documents = len(documents)
    words = {}
    for document in documents:
        seen = []
        for word in documents[document]:
            if word in seen:
                continue
            if word in words:
                words[word] += 1
            else:
                words[word] = 1
            seen.append(word)

    idfs = {}
    for word in words:
        idfs[word] = math.log(num_documents/words[word])

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tf_idfs = {}
    for file in files:
        total_value = 0
        for word in query:
            if word in files[file]:
                total_value += (files[file].count(word) * idfs[word])
    
        tf_idfs[file] = total_value

    tf_idfs_sorted = sorted(tf_idfs, key=lambda item: tf_idfs[item], reverse=True)

    return tf_idfs_sorted[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentences_ranked = {}
    for sentence in sentences:
        query_term_density = 0
        total_idfs = 0
        for word in query:
            if word in sentences[sentence]:
                query_term_density += 1
                total_idfs += idfs[word]
        sentences_ranked[sentence] = (total_idfs, query_term_density/(len(sentences[sentence])))

    ordered_sentences = sorted(sentences_ranked.items(), key=lambda item: item[1], reverse=True)
    new_order = []
    for sentence in ordered_sentences:
        new_order.append(sentence[0])

    return new_order[:n]


if __name__ == "__main__":
    main()
