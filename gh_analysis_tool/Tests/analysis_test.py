import os
import tempfile
from gh_analysis_tool.analysis import (
    calculate_unused_dep_scores,
    aggregate_score,
    dir_contains_requirements,
    prepare_options,
    format_results,
)


# Tests for calculate_unused_dep_scores
def test_calculate_unused_dep_scores_empty():
    """Test with empty dependency list"""
    mock_list_of_deps = []
    results = calculate_unused_dep_scores(mock_list_of_deps)
    assert results == 0


def test_calculate_unused_dep_scores_one_dep():
    """Test with 1 dependency"""
    mock_list_of_deps = [{'name': 'dep1', 'score': 1}]
    results = calculate_unused_dep_scores(mock_list_of_deps)
    assert results == 1


def test_calculate_unused_dep_scores_two_deps():
    """Test with 2 dependencies"""
    mock_list_of_deps = [{'name': 'dep1', 'score': 1}, {'name': 'dep2', 'score': 2}]
    results = calculate_unused_dep_scores(mock_list_of_deps)
    assert results == 1


def test_calculate_unused_dep_scores_three_deps():
    """Test with 3 dependencies"""
    mock_list_of_deps = [{'name': 'dep1'}, {'name': 'dep2'}, {'name': 'dep3'}]
    results = calculate_unused_dep_scores(mock_list_of_deps)
    assert results == 1


def test_calculate_unused_dep_scores_four_deps():
    """Test with 4 dependencies"""
    mock_list_of_deps = [{'name': 'dep1'}, {'name': 'dep2'}, {'name': 'dep3'}, {'name': 'dep4'}]
    results = calculate_unused_dep_scores(mock_list_of_deps)
    assert results == 2


def test_calculate_unused_dep_scores_five_deps():
    """Test with 5 dependencies"""
    mock_list_of_deps = [{'name': f'dep{i}'} for i in range(5)]
    results = calculate_unused_dep_scores(mock_list_of_deps)
    assert results == 2


def test_calculate_unused_dep_scores_six_deps():
    """Test with 6 dependencies"""
    mock_list_of_deps = [{'name': f'dep{i}'} for i in range(6)]
    results = calculate_unused_dep_scores(mock_list_of_deps)
    assert results == 3


# Tests for aggregate_score
def test_aggregate_score_zero():
    """Test aggregate_score with score 0"""
    result = aggregate_score(0)
    assert result == 'Low'


def test_aggregate_score_one():
    """Test aggregate_score with score 1"""
    result = aggregate_score(1)
    assert result == 'Medium'


def test_aggregate_score_three():
    """Test aggregate_score with score 3"""
    result = aggregate_score(3)
    assert result == 'Medium'


def test_aggregate_score_four():
    """Test aggregate_score with score 4"""
    result = aggregate_score(4)
    assert result == 'High'


def test_aggregate_score_five():
    """Test aggregate_score with score 5"""
    result = aggregate_score(5)
    assert result == 'High'


def test_aggregate_score_six():
    """Test aggregate_score with score 6"""
    result = aggregate_score(6)
    assert result == 'Unknown'


def test_aggregate_score_large():
    """Test aggregate_score with large score"""
    result = aggregate_score(100)
    assert result == 'Unknown'


# Tests for dir_contains_requirements
def test_dir_contains_requirements_true():
    """Test dir_contains_requirements when requirements.txt exists"""
    # Create a temporary directory with requirements.txt
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a requirements.txt file
        req_file = os.path.join(tmpdir, 'requirements.txt')
        with open(req_file, 'w') as f:
            f.write('pytest==1.0.0\n')
        
        result = dir_contains_requirements(tmpdir)
        assert result is True


def test_dir_contains_requirements_false():
    """Test dir_contains_requirements when requirements.txt does not exist"""
    # Create a temporary directory without requirements.txt
    with tempfile.TemporaryDirectory() as tmpdir:
        result = dir_contains_requirements(tmpdir)
        assert result is False


def test_dir_contains_requirements_other_files():
    """Test dir_contains_requirements with other files but no requirements.txt"""
    # Create a temporary directory with other files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some other files
        other_file = os.path.join(tmpdir, 'setup.py')
        with open(other_file, 'w') as f:
            f.write('# setup file\n')
        
        result = dir_contains_requirements(tmpdir)
        assert result is False


# Tests for prepare_options
def test_prepare_options():
    """Test prepare_options creates correct options object"""
    test_path = '/tmp/test_dir'
    opt = prepare_options(test_path)
    
    assert opt.requirements_filename == '/tmp/test_dir/requirements.txt'
    assert opt.paths == ['/tmp/test_dir']
    assert opt.ignore_modules is False
    assert opt.ignore_requirement is False
    assert opt.skip_incompatible is False


def test_prepare_options_different_path():
    """Test prepare_options with different path"""
    test_path = '/home/user/project'
    opt = prepare_options(test_path)
    
    assert opt.requirements_filename == '/home/user/project/requirements.txt'
    assert opt.paths == ['/home/user/project']


# Tests for format_results
def test_format_results_empty():
    """Test format_results with empty results"""
    results = []
    output = format_results(results)
    assert output == 'No results found'


def test_format_results_single():
    """Test format_results with single result"""
    results = [
        {'repo_name': 'test/repo1', 'final_score': 'Low'}
    ]
    output = format_results(results)
    assert 'test/repo1' in output
    assert 'Low' in output
    assert 'Repo Name' in output
    assert 'Security Risk' in output


def test_format_results_multiple():
    """Test format_results with multiple results"""
    results = [
        {'repo_name': 'test/repo1', 'final_score': 'Low'},
        {'repo_name': 'test/repo2', 'final_score': 'Medium'},
        {'repo_name': 'test/repo3', 'final_score': 'High'}
    ]
    output = format_results(results)
    assert 'test/repo1' in output
    assert 'test/repo2' in output
    assert 'test/repo3' in output
    assert 'Low' in output
    assert 'Medium' in output
    assert 'High' in output


def test_format_results_missing_final_score():
    """Test format_results when some results don't have final_score"""
    results = [
        {'repo_name': 'test/repo1', 'final_score': 'Low'},
        {'repo_name': 'test/repo2'}  # Missing final_score
    ]
    output = format_results(results)
    assert 'test/repo1' in output
    assert 'Low' in output
    # repo2 should not appear since it doesn't have final_score
    assert 'test/repo2' not in output
