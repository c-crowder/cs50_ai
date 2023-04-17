import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
NP -> N | ANP | CNP | DNP | PNP | NP VP | NP Adv
DNP -> Det N | Det ANP | Det PNP | Det CNP
ANP -> Adj N | Adj DNP | Adj PNP | Adj CNP | Adj ANP
PNP -> P N | P DNP | P ANP | P CNP
CNP -> Conj N | Conj DNP | Conj PNP | Conj ANP
VP -> V | Conj VP | VP NP 
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # tokenize a lowercase version of the sentence
    words = nltk.word_tokenize(sentence.lower())
    new_words = []
    for word in words:
        # Make sure that every word starts with a letter
        if word[0].isalpha():
            new_words.append(word)

    # return valid tokenized words
    return new_words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # Helper function that checks recursively if the given tree structure contains any 'NP' chunks
    def contains_np(tree):
        if tree.label() not in ['S', 'NP', 'DNP', 'ANP', 'PNP', 'CNP', 'VP']:
            return False
        elif tree.label() == 'NP':
            return True
        for t in tree.subtrees():
            if t == tree:
                continue
            if contains_np(t):
                return True
        return False

    # Initialize variables to capture the chunks to be returned, the nodes to check, and the trees of the subtree
    chunks = []
    nodes = []
    trees = tree.subtrees(lambda t: t.label() == 'NP')
    for tree in trees:
        nodes.append(tree)

    # While there is something in nodes, remove an item from it and check if it is a noun phrase chunk
    # it is a noun phrase chunk if it is labeled a noun phrase, and none of its subtrees contain noun phrases
    # Trees that do not fit the criteria are either expanded if they are noun phrases or discarded of
    while nodes:
        tree = nodes.pop()
        if tree.label() == 'NP':
            valid = True
            for t in tree.subtrees():
                if t == tree:
                    continue
                contains = contains_np(t)
                if contains:
                    valid = False
                    nodes.append(t)
            # Make sure to not include duplicates and add all valid NP_Chunks to the list
            if valid and tree not in chunks:
                chunks.append(tree)

    return chunks


if __name__ == "__main__":
    main()
