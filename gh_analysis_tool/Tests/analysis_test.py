from gh_analysis_tool.analysis import calculate_unused_dep_scores


# TODO: there should be more tests here to cover all known cases

def test_calculate_unused_dep_scores():
    mock_list_of_deps = [{'name': 'dep1', 'score': 1}, {'name': 'dep2', 'score': 2}]
    results = calculate_unused_dep_scores(mock_list_of_deps)
    assert results == 1


def test_calculate_unused_dep_scores_empty():
    mock_list_of_deps = []
    results = calculate_unused_dep_scores(mock_list_of_deps)
    assert results == 0
