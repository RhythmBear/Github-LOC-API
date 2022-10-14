import requests

# This is my API to get the total lines of code in my github repository

LOC_URL = "https://api.codetabs.com/v1/loc"
USER = "RhythmBear"


def get_lines_for_repo(github_account: str, repo_name: str):
    """ Get the total lines of code per repository """

    params = {"github": f"{github_account}/{repo_name}"}

    # Try to raise test for any possible errors while handling this request.
    try:
        response = requests.get(LOC_URL, params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    try:
        total_response = response.json()[-1]
        lines_of_code = total_response["linesOfCode"]
    except IndexError:
        lines_of_code = 0

    return lines_of_code


# Get the names of all the repositories in a github account.
repo_url = f"https://api.github.com/users/{USER}/repos"

repo_response = requests.get(repo_url)
# print(repo_response.json())

# For each reository in the response, Get the name of the repository and pass it into the get the lines function
results = {}
total_lines = 0
for item in repo_response.json():
    repository_name = item['name']
    lines_result = get_lines_for_repo(USER, repository_name)
    total_lines += lines_result

    # Append the result to result dictionary
    results[repository_name] = lines_result

results['total_lines'] = total_lines

print(results)
print(total_lines)
