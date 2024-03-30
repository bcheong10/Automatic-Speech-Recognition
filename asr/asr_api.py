from flask import Flask, request, jsonify
import soundfile as sf
import torch
from datasets import load_dataset
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import librosa
import os

# load pretrained model
# processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
# model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")

processor = None
model = None

def model_inference(model_name, file_path):

    global processor, model

    # Check if model and processor are already loaded
    if model is None or processor is None:
        # Load the model and processor
        processor = Wav2Vec2Processor.from_pretrained(model_name)
        model = Wav2Vec2ForCTC.from_pretrained(model_name)
        print("Loaded!")

    # get audio duration
    info = sf.info(file_path)
    duration = info.duration

    # Breaks the audio into chunks if the duration is greater than 30 seconds for easier computation
    if duration > 30:
        # Define chunk size
        chunk_size_seconds = 10
        chunk_size_samples = chunk_size_seconds * 16000

        # load audio
        audio_input, sample_rate = sf.read(file_path)
        audio_resampled = librosa.resample(audio_input, orig_sr=sample_rate, target_sr=16000)

        # Process each chunk separately
        transcription = ""
        for i in range(0, len(audio_resampled), chunk_size_samples):
            chunk = audio_resampled[i:i+chunk_size_samples]

            # Tokenize and transcribe the chunk
            input_values = processor(chunk, return_tensors="pt", sampling_rate=16000).input_values
            with torch.no_grad():
                logits = model(input_values).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            chunk_transcription = processor.batch_decode(predicted_ids)
            transcription += chunk_transcription[0] + " "

    else:
        # load audio
        audio_input, sample_rate = sf.read(file_path)
        audio_resampled = librosa.resample(audio_input, orig_sr=sample_rate, target_sr=16000)

        input_values = processor(audio_resampled, sampling_rate=16000, return_tensors="pt").input_values

        # retrieve logits & take argmax
        logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)

        # transcribe
        transcription = processor.decode(predicted_ids[0])


    return transcription, duration


# API Call
app = Flask(__name__)

@app.route('/asr', methods=['POST'])
def transcribe_audio():

    model_name = "facebook/wav2vec2-large-960h"

    # Check if the 'file' parameter is present in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    # Get the audio file from the request
    audio_file = request.files['file']

    # Save the audio file to a temporary location
    temp_file_path = 'temp.mp3'
    audio_file.save(temp_file_path)

    # Call the model inference function
    transcription, duration = model_inference(model_name, temp_file_path)

    # Delete the temporary audio file
    os.remove(temp_file_path)

    # Return the transcription and duration in JSON format
    response = {
        'transcription': transcription,
        'duration': str(duration)
    }

    return jsonify(response), 200, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
