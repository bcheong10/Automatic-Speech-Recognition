import os
import requests
import pandas as pd
import time

def transcribe_audio_file(audio_file_path, api_url):
    # Read the audio file
    with open(audio_file_path, 'rb') as file:
        audio_data = file.read()

    # Send a POST request to the API endpoint with the audio data
    response = requests.post(api_url, files={'file': audio_data}, timeout=100)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print(f"Transcribing {audio_file_path})")
        return response.json()
    else:
        # Print an error message if the request was not successful
        print(f"Error: Failed to transcribe {audio_file_path}")
        return "Failed to transcribe"

# Write transcription and duration to a CSV file
def transcription_to_csv(index, csv_file, trascriptions, duration):

    df = pd.read_csv(csv_file)

    df.loc[index, 'generated_text'] = trascriptions
    df.loc[index, 'duration'] = duration

    df.to_csv(csv_file, index=False)

    print(f"CSV Updated!")



if __name__ == "__main__":
    # Specify the API URL
    api_url = "http://localhost:8001/asr"  

    # Specify the directory containing the audio files
    audio_files_dir = "common_voice/cv-valid-dev/cv-valid-dev"

    index = 2557

    csv_file = "cv-valid-dev.csv"

    # Iterate over each file in the directory
    for audio_file in os.listdir(audio_files_dir)[index:]:
        
        audio_file_path = os.path.join(audio_files_dir, audio_file)

        # Call the transcribe_audio_file function to transcribe the audio file
        result = transcribe_audio_file(audio_file_path, api_url)

        transcription_result = result['transcription']
        duration_result = result['duration']

        # function is called every audio file transcription in case of data loss due to error
        transcription_to_csv(index, csv_file, transcription_result, duration_result)

        index += 1
    
