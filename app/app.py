from flask import Flask, render_template, jsonify, request
import random
import csv
import io
from fetch_results import *

app = Flask(__name__)

WINNERS_FILE = 'winners.txt'

def get_previous_winners():
    try:
        with open(WINNERS_FILE, 'r') as f:
            winners = f.read().strip().split(',')
            return set(int(winner) for winner in winners if winner)
    except FileNotFoundError:
        return set()

def add_winner(winner):
    with open(WINNERS_FILE, 'a') as f:
        f.write(f"{winner},")

def get_unique_winners(numbers, previous_winners, num_people):
    unique_numbers = list(set(numbers) - previous_winners)
    if len(unique_numbers) < num_people:
        raise ValueError("Not enough unique PF numbers left to select.")
    return random.sample(unique_numbers, num_people)

def fisher_yates_shuffle(arr):
    for i in range(len(arr) - 1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

def parse_str_data(data_string: str):
    # Parsing CSV string
    f = io.StringIO(data_string)
    reader = csv.DictReader(f, delimiter=';')

    # Convert to a list of dictionaries
    data_list = [row for row in reader]
    return data_list

def extract_values_with_pf(data):
    pf_values = []
    # Assuming 'pf' keys are not common and dataset is not huge
    for item in data:
        # Convert keys to lowercase once per item
        lower_case_keys = {k.lower(): v for k, v in item.items()}
        for key in lower_case_keys:
            if 'pf' in key:
                pf_values.append(lower_case_keys[key])
                # Remove break if you need all 'pf' occurrences
                # break

    return pf_values if pf_values else "Anonymous Survey"

def get_data(survey_id:int):
    # get session key
    username = "pluginManager"
    password = "w4Gu6ctRvCHm"
    session = MPulseSessionManager(username, password, base_url="https://mpulse.maybanksandbox.com")
    session_key = session.get_session_key()

    # run api to get survey responses

    api = MPulseAPI()
    method = "export_responses"
    params = [session_key, survey_id, "csv", "en", "all", "full"] # survey_id = 926839

    response = api.make_request(method, params)

    if response.status_code == 200:
        # print(response.text)
        response_data = response.json()
        results = Process.decode_base64_from_dict(response_data)
        print(results)
        # Extracting the values
        numbers = extract_values_with_pf(parse_str_data(results)) #pf_values
        numbers = [int(number) for number in numbers]
        print(numbers)
        return numbers
        
    else:
        print("Request failed with status code", response.status_code)
        # return f'Request failed with status code {response.status_code}'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shuffle', methods=['POST'])
def shuffle():
    survey_id = request.form.get('survey_id')
    num_people = int(request.form.get('num_people', 1))
    previous_winners = get_previous_winners()

    numbers = get_data(int(survey_id)) if survey_id else []
    if numbers:
        try:
            # Select unique winners
            selected_numbers = get_unique_winners(numbers, previous_winners, num_people)
            # Add new winners to the list of previous winners
            for winner in selected_numbers:
                add_winner(winner)
            return jsonify({'numbers': selected_numbers})
        except ValueError as e:
            return jsonify({'error': str(e)})
    else:
        return jsonify({'error': 'No PF numbers found or not enough unique PF numbers'})


if __name__ == '__main__':
    app.run(debug=True)
