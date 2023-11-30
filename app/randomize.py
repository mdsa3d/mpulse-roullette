import streamlit as st
import io
import csv
import random
from fetch_results import *

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
    session = MPulseSessionManager(username, password, base_url="https://mpulse-dev.maybanksandbox.com")
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


# Title of the app
st.title('M-Pulse Raffle')

# User inputs
survey_id = st.text_input('Enter the survey id:')
num_people = st.number_input('How many numbers to select?', min_value=1, step=1)

# Button to trigger the selection
if st.button('Shuffle'):
    numbers = get_data(survey_id)
    if numbers:
        # Shuffle the list using Fisher-Yates
        shuffled_list = fisher_yates_shuffle(numbers)

        # Select the first n numbers
        selected_numbers = shuffled_list[:num_people]

        # Display the selected numbers
        st.write('Selected Numbers:', selected_numbers)
    else:
        st.write('Please choose different survey ID.')
