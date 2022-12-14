import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from DateTime.DateTime import datetime as dt
import time

#universal format for date = 'YYYY-MM-DD'


# This is my API to get the total lines of code in my github repository

LOC_URL = "https://api.codetabs.com/v1/loc"
# USER = "RhythmBear"

# ------------------- FUNCTIONS -----------------------------------------------------------


def days_between(last_date: str):
    """
    This function takes in a date input in the format yyyy-mm-dd and returns the number of days
    between the given date and the current date.
    :param last_date:
    :return:
    """
    today_date = dt.now().date()
    # print(f"today's date is {today_date}")
    previous_date = dt(int(last_date.split('-')[0]), int(last_date.split('-')[1]), int(last_date.split('-')[2])).date()
    days_between = today_date - previous_date
    days_between = days_between.days
    # print(f"There are {days_between} days between {today_date} and {previous_date}. ")

    return days_between


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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loc_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKrfb'
# Create database
db = SQLAlchemy(app)


class GithubLines(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    lines_of_code = db.Column(db.Integer, nullable=True, unique=False)
    date_updated = db.Column(db.String(25), nullable=False)


#db.create_all()

# ---------------------- DEFINING ROUTES ------------------------------------------------------------


@app.route("/")
def home():
    resp = {'success': False,
            'message': "Please pass in github username in url e.g https://thisaddress.com/<your-github-username>"}
    return jsonify(
        resp
    )


@app.route("/<user>", methods=["GET"])
def get_lines(user):
    start_time = time.time()
    print(request.args)
    # Search the Database to check if the data exists there
    user_repo = GithubLines.query.filter_by(username=user).first()

    if user_repo:
        print(user_repo)
        if days_between(user_repo.date_updated) < 30:
            answer = {
                'response': f"Successfully Retrieved lines of Code for {user} from cache in {time.time() - start_time}seconds",
                'Total lines': user_repo.lines_of_code,
                'Repositories': []
            }
            return jsonify(answer)

        # If the user exists and

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
        # Check to make sure we are not getting forked repositories
        if item['fork']:
            continue
        else:
            repository_name = item['name']
            lines_result = get_lines_for_repo(user, repository_name)
            total_lines += lines_result

        # Append the result to result dictionary
        results[repository_name] = lines_result

    answer = {
        'response': f"Successfully Retrieved lines of Code for {user} in {int(time.time() - start_time)}seconds",
        'Total lines': total_lines,
        'Repositories': results
    }
    print(answer)

    # If Entry is not in the database, Add it and if it is, Append it.
    if user_repo:
        user_repo.date_updated = dt.now().date()
        db.session.commit()
    else:
        new_user = GithubLines(username=user,
                               lines_of_code=total_lines,
                               date_updated=dt.now().date())
        db.session.add(new_user)
        db.session.commit()

    return jsonify(
        answer
    )


if __name__ == "__main__":
   app.run(debug=True, port=80)
