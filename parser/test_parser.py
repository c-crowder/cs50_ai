from parser import preprocess


def test_preprocess():
    assert preprocess(".") == []
    assert preprocess("Hi my name is Bob") == ["hi", "my", "name", "is", "bob"]
    assert preprocess("Mr. John") == ["mr.", "john"]
    assert preprocess("one 28 plus 3") == ["one", "plus"]