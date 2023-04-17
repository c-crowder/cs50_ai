from pagerank import *

def test_transition_model():
    for corpus_num in [0,1,2]:
        corpus = crawl(f"corpus{corpus_num}")
        for corp_page in corpus:
            model = transition_model(corpus, corp_page, .85)
            total = 0
            for page in model:
                total += model[page]
            # if not total == 1:
            #     print (total)
            #     print(model)
            #     print(corp_page)
            #     print(corpus)
            assert round(total, 3) == 1

def test_sample_pagerank():
    for corpus_num in [0,1,2]:
        corpus = crawl(f"corpus{corpus_num}")
        page_rank = sample_pagerank(corpus, .85, 10000)
        total = 0
        for page in page_rank:
            total += page_rank[page]
        if .999 < total < 1.001:
            total = 1
        assert round(total, 3) == 1

def test_iterate_pagerank():
    for corpus_num in [0,1,2]:
        corpus = crawl(f"corpus{corpus_num}")
        page_rank = iterate_pagerank(corpus, .85)
        total = 0
        for page in page_rank:
            total += page_rank[page]
    
        if .999 < total < 1.001:
            total = 1
        assert round(total, 3) == 1

if __name__ == "__main__":
    test_transition_model()
    test_sample_pagerank()
    test_iterate_pagerank()
