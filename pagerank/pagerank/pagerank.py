import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Dictionary to keep track of the distribution to be returned
    probability_distribution = {}

    # Verify that the provide page is in the corpus, and track the links associated with that page
    if page in corpus:
        links = corpus[page]
    else:
        return
    # If there are links on the page, then assign a damping for each link based on the length of links and damping factor
    # Assign a damping for everything based on the length of everything and inverse of damping factor
    # Otherwise, the total damping is just 1/len(everything)
    if len(links) != 0:
        linked_damping_each = damping_factor/len(links)
        total_damping_each = (1-damping_factor)/len(corpus)
    else:
        linked_damping_each = 0
        total_damping_each = (1)/len(corpus)
    
    # For each link, assign the corresponding damping factor
    for link in links:
        probability_distribution[link] = linked_damping_each + total_damping_each

    # assign damping for the assigned page
    probability_distribution[page] = total_damping_each

    # Assign the damping for everything else in the corpus
    for pages in corpus:
        if pages not in probability_distribution:
            probability_distribution[pages] = total_damping_each

    return probability_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Create variables to keep track of counts for each link and pages
    link_count = {}
    pages = []
    # append all the pages and set all the counts to 0
    for page in corpus:
        pages.append(page)
        link_count[page] = 0
    # Choose one page from the corpus at random with equal probability
    starting_page = random.choice(pages)

    # From each page, based on the transition model, assign new weights to each page
    # Choose a new page based on these new weights, and add a count for the page we started on
    # Reassign "starting_page" to the new page we chose, and repeat the process for as many times as there are samples
    i = 0
    while i < n-1:
        link_count[starting_page] += 1
        new_model = transition_model(corpus, starting_page, damping_factor)
        pages = []
        page_weights = []
        for page in new_model:
            pages.append(page)
            page_weights.append(new_model[page])
        starting_page = random.choices(pages, weights=page_weights, k=1)[0]
        i += 1
    # Find the percentage variable of each page count by dividing each count by the total # of samples
    for page in link_count:
        link_count[page] /= n

    return link_count
    

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Assign variables to keep track of all the pages, the ranks, a comparable ranks (for detecting the change),
    # and the number of links for each page
    pages = []
    page_ranks = {}
    compared_page_ranks = {}
    num_links = {}
    
    # Assign starting values to variable above based on the assumption that all page ranks are chosen equally
    for page in corpus:
        page_ranks[page] = 1/len(corpus)
        compared_page_ranks[page] = 1/len(corpus)
        pages.append(page)
        if corpus[page] == set():
            for paged in corpus:
                corpus[page].add(paged)
        num_links[page] = len(corpus[page])

    # While there is no change between page_ranks and compared_page_ranks greater than 1/1000th,
    # Repeat the following:
    """
    Determind the probability that you would land on the current page from any other given page 
    based on the page ranks and whether the current page is being linked to
    Do this for every page to find new page rank values and assign them to 
    compared_page_rank - this what we compare to check the change from the previous version
    if it converged by 1/1000ths, we return the value
    """
    while True:
        # Set new page rank values
        for page in pages:
            page_links = [linked for linked in corpus if page in corpus[linked]]

            sum_link_prob = 0
            for link in page_links:
                
                prob_from_link = page_ranks[link]/num_links[link]
                sum_link_prob += prob_from_link
                
            compared_page_ranks[page] = (1-damping_factor)/len(corpus) + (damping_factor * sum_link_prob)

        # If it did not converge, set to False  
        changed = True
        for page in page_ranks:
            if format(page_ranks[page], ".6f") != format(compared_page_ranks[page], ".6f"):
                changed = False

        # If it coverged, return the value
        if changed:
            return compared_page_ranks
        # Otherwise, set page ranks equal
        else:
            for page in page_ranks:
                page_ranks[page] = compared_page_ranks[page]



if __name__ == "__main__":
    main()
