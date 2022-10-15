import requests
from flask import Flask, jsonify, render_template, request


# This is my API to get the total lines of code in my github repository

LOC_URL = "https://api.codetabs.com/v1/loc"
# USER = "RhythmBear"


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


# Flask API_KEY
app = Flask(__name__)


@app.route("/<user>")
def get_lines(user):
    print(request.args)

    # Get the names of all the repositories in a github account.

    repo_url = f"https://api.github.com/users/{user}/repos"

    repo_response = requests.get(repo_url)
    repo_response_json = repo_response.json()

    print(repo_response_json)
    try:
        print(type(repo_response_json))
        if type(repo_response_json) == dict:
            return jsonify(
                {'Response': f"Failed to locate Github Account with Username {user}."}

            )
        else:
            pass
    except KeyError or TypeError:
        pass


    # For each repository in the response, Get the name of the repository and pass it into the get the lines function
    results = {}
    total_lines = 0
    for item in repo_response.json():
        repository_name = item['name']
        lines_result = get_lines_for_repo(user, repository_name)
        total_lines += lines_result

        # Append the result to result dictionary
        results[repository_name] = lines_result

    answer = {
        'response': f"Successfully Retrieved lines of Code for {user}",
        'Total lines': total_lines,
        'Repositories': results
    }
    print(answer)

    return jsonify(
        answer
    )


if __name__ == "__main__":
   app.run()
