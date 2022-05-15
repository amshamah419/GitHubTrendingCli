import os
import sys

import click
import github
import tempfile
import shutil
import logging

from halo import Halo
from gtrending import fetch_repos
from git import Repo
from pip_check_reqs.find_extra_reqs import find_extra_reqs
from prettytable import PrettyTable


@click.group(chain=True)
def main():
    pass


@main.command()
@click.help_option(
    '-h', '--help'
)
@click.option(
    '-n', '--num_to_search', help='The number of repositories to inspect.', required=True
)
@click.option(
    '-g', '--github_access_token', help='Your personal access token from Github.', required=True
)
def analyze(**kwargs):
    num_to_return = int(kwargs.get('num_to_search', '0'))
    github_access_token = kwargs.get('github_access_token', '')
    if num_to_return > 25:
        logging.error('The limit is 25')
        return
    spinner = Halo(text=f'Processing {num_to_return} trending repositories', spinner='dots')
    spinner.start()
    github_client = github.Github(login_or_token=github_access_token)
    results: list = list()
    trending_results = get_github_trending_results(num_to_return=num_to_return)
    for tending_result in trending_results:
        repo_info = get_repo_info(full_repo_name=tending_result.get('fullname'), github_client=github_client)
        results.append(repo_info)

    result_string = format_results(results=results)
    print(result_string)
    spinner.stop()
    sys.exit(0)


class options:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.requirements_filename = None
        self.paths = []
        self.ignore_modules = False
        self.ignore_requirement = False
        self.skip_incompatible = False

    @staticmethod
    def ignore_files(input_filename):
        return False

    @staticmethod
    def ignore_mods(input_filename):
        return False

    @staticmethod
    def ignore_reqs(input_filename):
        return False


def aggregate_score(score: int) -> str:
    """
    Aggregate the scores
    :param score:
    :return:
    """
    if score == 0:
        return 'Low'
    elif score <= 3:
        return 'Medium'
    elif score <= 5:
        return 'High'
    return 'Unknown'


def calculate_unused_dep_scores(deps: list) -> int:
    """
    Calculate the risk score based on dependencies
    :param deps:
    :return:
    """
    items_in_deps = len(deps)
    if items_in_deps == 0:
        return 0
    elif items_in_deps <= 3:
        return 1
    elif items_in_deps <= 5:
        return 2
    return 3


def dir_contains_requirements(dirpath: str) -> bool:
    """
    Check if the directory contains a requirements.txt
    :param dirpath:
    :return:
    """
    return 'requirements.txt' in os.listdir(dirpath)


def prepare_options(dirpath: str) -> options:
    """
    The pip-check-reqs package requires options to be passed in. This function creates the options object.
    :return: options object
    """
    opt = options()
    opt.requirements_filename = dirpath + '/requirements.txt'
    opt.paths = [dirpath]
    return opt


def get_github_trending_results(num_to_return: int):
    """
    Get the found_repos from github
    :param num_to_return:
    :return:
    """

    found_repos = fetch_repos('python', 'en')
    return [x for index, x in enumerate(found_repos) if index < num_to_return]


def get_repo_info(full_repo_name: str, github_client: github.Github) -> dict:
    repository = github_client.get_repo(full_repo_name)
    clone_url = repository.clone_url
    logging.info(f'Fetching {full_repo_name} - {clone_url}')
    dirpath = tempfile.mkdtemp()
    Repo.clone_from(clone_url, dirpath)
    try:
        if dir_contains_requirements(dirpath):
            opt = prepare_options(dirpath)
            res = find_extra_reqs(options=opt, requirements_filename=opt.requirements_filename)
            dep_score = calculate_unused_dep_scores(res)
            final_score = aggregate_score(dep_score)
            result = {
                'repo_name': full_repo_name,
                'final_score': final_score,
            }
            return result

    except Exception as e:
        logging.error(f'Error: {e}')
    shutil.rmtree(dirpath)
    return {}


def format_results(results: list) -> str:
    """
    Format the results
    :param results: list of dicts containing repo_name and final_score
    :return: results string
    """
    if len(results) == 0:
        return 'No results found'
    table = PrettyTable(['Repo Name', 'Security Risk'])
    for result in results:
        if 'final_score' in result:
            table.add_row([result.get('repo_name'), result.get('final_score')])

    return table.get_string()


if __name__ == '__main__':
    main()
