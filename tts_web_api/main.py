import json
import os
import io
import vits_tts
import time
from scipy.io import wavfile
from flask import Flask, request, Response, jsonify, send_file, url_for

app = Flask(__name__)

AUDIO_FILES_DIR = 'audio_files'
os.makedirs(AUDIO_FILES_DIR, exist_ok=True)

@app.route('/models')
def models():
    models = [model for model in os.listdir('models') if os.path.isdir(os.path.join('models', model))]
    return jsonify(models)

@app.route('/models/<model_name>/speakers')
def speakers(model_name):
    config_path = os.path.join('models', model_name, 'moegoe_config.json')
    if not os.path.exists(config_path):
        return jsonify({"error": "moegoe_config.json is not found"}), 404

    with open(config_path, 'r') as f:
        config = json.load(f)
        speakers = [{"id": i, "name": speaker} for i, speaker in enumerate(config['speakers'])]

    return jsonify(speakers)

@app.route('/models/<model_name>/speakers/<speaker_id>', methods=['POST'])
def tts(model_name, speaker_id):
    try:
        model = vits_tts.load_model(model_name)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    if model is None:
        return jsonify({"error": "model not found"}), 404

    if int(speaker_id) not in model["speakers_ids"].keys():
        return jsonify({"error": "speaker_id not found", "speakers_ids": model["speakers_ids"]}), 404

    if 'text' not in request.json:
        return jsonify({"error": "text is required"}), 422

    model["last_used"] = time.time()
    language = request.json.get('language', None)
    speed = request.json.get('speed', 0.95)
    noise_scale = request.json.get('noise_scale', .667)
    noise_scale_w = request.json.get('noise_scale_w', 0.8)

    audio_result = model["tts_fn"](request.json['text'], speaker_id, language, speed, noise_scale, noise_scale_w)
    if audio_result[0] != "Success":
        return jsonify({"error": "convert fail"}), 500

    filename = f"{time.time()}_{model_name}_{speaker_id}.wav"
    filepath = os.path.join(AUDIO_FILES_DIR, filename)
    wavfile.write(filepath, audio_result[1][0], audio_result[1][1])

    file_url = url_for('get_audio_file', filename=filename, _external=True)
    return jsonify({"url": file_url})

@app.route('/audio_files/<filename>')
def get_audio_file(filename):
    return send_file(os.path.join(AUDIO_FILES_DIR, filename), mimetype='audio/wav')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3232)
