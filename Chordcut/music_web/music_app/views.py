from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse
from .models import *

def index_page(request):
    return render(request, "index.html")

def login_page(request):
    return render(request, "login.html")

def home_page(request):
    return render(request, "home.html")

def about_page(request):
    return render(request, "about.html")

def contact_page(request):
    return render(request, "contact.html")

def service_page(request):
    return render(request, "searvices.html")

def seprate_page(request):
    return render(request, "music_seprate_page.html")

def remix_page(request):
    return render(request, "music_remix.html")

def combaine_page(request):
    return render(request, "music_combain.html")


def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name') 
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirmation = request.POST.get('confirm_password')  
        mobile = request.POST.get('phone_number')

        if not full_name or not email or not password or not password_confirmation or not mobile:
            return HttpResponse("<script>alert('All fields are required');window.location.href='/login_page/';</script>")

        if password != password_confirmation:
            return HttpResponse("<script>alert('Passwords do not match');window.location.href='/login_page/';</script>")

        if UserProfile.objects.filter(contact_email=email).exists():
            return HttpResponse("<script>alert('Email is already registered');window.location.href='/login_page/';</script>")

        if UserProfile.objects.filter(contact_number=mobile).exists():
            return HttpResponse("<script>alert('Mobile number is already registered');window.location.href='/login_page/';</script>")

        user = UserProfile(
            full_name=full_name, 
            contact_email=email, 
            user_password=password, 
            contact_number=mobile
        )
        user.save()

        return HttpResponse("<script>alert('Registration Successful!');window.location.href='/login_page/';</script>")

    return render(request, 'login.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email,password)
        try:
            user = UserProfile.objects.get(contact_email=email, user_password=password)
        except UserProfile.DoesNotExist:
            return HttpResponse("<script>alert('Invalid email or password!');window.location.href='/login/';</script>")

        request.session['email'] = user.contact_email
        request.session['user_id'] = user.user_id 
        return HttpResponse("<script>alert('User Login Successful');window.location.href='/home_page/';</script>")

    return render(request, 'login.html')



def logout(request):
    request.session.flush() 
    return render(request, "index.html")


from django.shortcuts import render
from django.http import HttpResponse
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import shutil
from music_web.settings import *
import numpy as np
import tensorflow as tf
from scipy.io import wavfile
from scipy.signal import resample
from music_web.settings import *
import os
import shutil
from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


import traceback  # Add this to capture errors

# handles the process of separating audio components from an 
# uploaded audio file and download the extracted components.
def audio_separation_view(request):
    # audio file is taken from music seprate page input
    if request.method == "POST" and request.FILES.get("audioFile"):
        try:
            audio_file = request.FILES["audioFile"]
            selected_component = request.POST.get("audioComponent", "all")

            file_path = default_storage.save(f"uploads/{audio_file.name}", ContentFile(audio_file.read()))
            temp_input_path = default_storage.path(file_path)

            output_dir = os.path.join("media", "separated_audio", os.path.splitext(audio_file.name)[0])
            os.makedirs(output_dir, exist_ok=True)
            print(output_dir)
            model_paths = {
            "drums": "best_model_drums.h5",
            "vocals": "best_model_vocals.h5",
            "others": "best_model_others.h5",
            "bass": "best_model_bass.h5"
        }

            predict_sources(temp_input_path, output_dir,model_paths)
          
            temp_filename = os.path.basename(temp_input_path)
            base_filename = os.path.splitext(temp_filename)[0]
            output_dir = os.path.join(output_dir,base_filename)
            print(output_dir)
            output_audio_paths = {
                "vocals": os.path.join(output_dir, "vocals.wav"),
                "drums": os.path.join(output_dir, "drums.wav"),
                "bass": os.path.join(output_dir, "bass.wav"),
                "others": os.path.join(output_dir, "other.wav"),
            }
            if selected_component == "all":
                zip_file = shutil.make_archive(output_dir, 'zip', output_dir)
                with open(zip_file, 'rb') as f:
                    response = HttpResponse(f.read(), content_type="application/zip")
                    response["Content-Disposition"] = 'attachment; filename="separated_audio.zip"'
            elif selected_component in output_audio_paths:
                with open(output_audio_paths[selected_component], 'rb') as f:
                    response = HttpResponse(f.read(), content_type="audio/wav")
                    response["Content-Disposition"] = f'attachment; filename="{selected_component}.wav"'
            else:
                response = HttpResponse("Invalid selection", status=400)

            os.remove(temp_input_path)
            return response

        except Exception as e:
            error_message = f"Error occurred: {str(e)}\n{traceback.format_exc()}"
            return HttpResponse(error_message, status=500)

    return render(request, "music_seprate_page.html")


# 16000hz sampling rate is taken (16000 snapshots are taken or details are taken from sound per second)


def preprocess_audio(file_path, target_sampling_rate=16000, chunk_size=64):
    sr, audio = wavfile.read(file_path)

    if sr != target_sampling_rate:
        audio = resample(audio, int(len(audio) * target_sampling_rate / sr))
        sr = target_sampling_rate

    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)

    audio = audio / np.max(np.abs(audio))

    audio_chunks = [audio[i:i + chunk_size] for i in range(0, len(audio) - chunk_size + 1, chunk_size)]

    return np.expand_dims(np.array(audio_chunks), -1), sr


def reconstruct_audio(chunks):
    return np.concatenate(chunks, axis=0)


def predict_source(input_file, output_files, model_paths):
    models = {source: tf.keras.models.load_model(path, compile=False) for source, path in model_paths.items()}

    x_input, sr = preprocess_audio(input_file)

    predictions = {source: models[source].predict(x_input) for source in models}

    for source, y_pred in predictions.items():
        predicted_audio = reconstruct_audio(y_pred.squeeze())
        predicted_audio = np.int16(predicted_audio * 32767)
        wavfile.write(output_files[source], sr, predicted_audio)


from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import librosa
import numpy as np
import soundfile as sf
import os

def load_audio(file_path):
    y, sr = librosa.load(file_path, sr=None)
    return y, sr

def apply_pitch_shift(y, sr, n_steps=2):
    return librosa.effects.pitch_shift(y, sr, n_steps)

def apply_hpss(y):
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    return y_harmonic, y_percussive

def apply_echo(y, sr, echo_level=0.4, delay=0.3):
    delay_samples = int(delay * sr)
    echo_signal = np.zeros_like(y)
    echo_signal[delay_samples:] = y[:-delay_samples]
    y_echo = y + echo_level * echo_signal
    return y_echo

def remix_audio(input_folder, output_folder, music_folder, remix_option):
    os.makedirs(output_folder, exist_ok=True)
    
    components = ['vocals', 'drums', 'bass', 'other']
    final_mixed_audio = None
    print(input_folder)
    print(music_folder)
    for component in components:
        component_path = os.path.join(input_folder, f"{component}.wav")
        
        if not os.path.exists(component_path):
            print(f"Warning: {component_path} not found, skipping.")
            continue
        
        y, sr = load_audio(component_path)
        
        if remix_option == "pitch_shift":
            y = apply_pitch_shift(y, sr)
        elif remix_option == "hpss":
            y_harmonic, y_percussive = apply_hpss(y)
            y = y_harmonic + y_percussive
        elif remix_option == "echo":
            y = apply_echo(y, sr)
        elif remix_option == "all":
            y_pitch_shifted = apply_pitch_shift(y, sr)
            y_harmonic, y_percussive = apply_hpss(y)
            y_echo = apply_echo(y, sr)
            y = y_harmonic + y_percussive + y_pitch_shifted + y_echo
            y = y / np.max(np.abs(y))
        
        if final_mixed_audio is None:
            final_mixed_audio = y
        else:
            final_mixed_audio += y
    
    final_mixed_audio = final_mixed_audio / np.max(np.abs(final_mixed_audio))
    
    output_file_path = os.path.join(output_folder, f"{music_folder}_final_remixed.wav")
    sf.write(output_file_path, final_mixed_audio, sr)
    return output_file_path

def audio_remix(request):
    if request.method == "POST" and request.FILES.get("audioFile"):
        audio_file = request.FILES["audioFile"]
        remix_option = request.POST.get("remixOption", "all")
        print(remix_option)
        file_path = default_storage.save(f"uploads/{audio_file.name}", ContentFile(audio_file.read()))
        temp_input_path = default_storage.path(file_path)

        output_dir = os.path.join("media", "separated_audio", os.path.splitext(audio_file.name)[0])
        os.makedirs(output_dir, exist_ok=True)

        model_paths = {
            "drums": "best_model_drums.h5",
            "vocals": "best_model_vocals.h5",
            "others": "best_model_others.h5",
            "bass": "best_model_bass.h5"
        }

        predict_sources(temp_input_path, output_dir, model_paths)
        temp_filename = os.path.basename(temp_input_path)
        base_filename = os.path.splitext(temp_filename)[0]
        output_dir = os.path.join(output_dir, base_filename)
        
        remix_output_folder = os.path.join("media", "remixed_audio")
        remixed_audio_path = remix_audio(output_dir, remix_output_folder, base_filename, remix_option)
        
        with open(remixed_audio_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="audio/wav")
            response["Content-Disposition"] = f'attachment; filename="{os.path.splitext(audio_file.name)[0]}_remixed.wav"'
        
        os.remove(temp_input_path)
        return response

    return render(request, "music_seprate_page.html")



def audio_combine(request):
    if request.method == 'POST' and request.FILES.get('audioFile1') and request.FILES.get('audioFile2'):
        audio_file1 = request.FILES['audioFile1']
        audio_file2 = request.FILES['audioFile2']
        remix_option = request.POST.get('remixOption')

        # Save uploaded audio files
        file_path1 = default_storage.save('audio1.wav', audio_file1)
        file_path2 = default_storage.save('audio2.wav', audio_file2)

        # Load audio files
        y1, sr1 = load_audio(file_path1)
        y2, sr2 = load_audio(file_path2)

        # Ensure both audios have the same sample rate
        if sr1 != sr2:
            return HttpResponse("Sample rates of both audio files must match.", status=400)

        # Apply remix effects
        if remix_option == 'pitch_shift':
            remixed_audio1 = apply_pitch_shift(y1, sr1)
            remixed_audio2 = apply_pitch_shift(y2, sr2)
        elif remix_option == 'hpss':
            remixed_audio1, _ = apply_hpss(y1)
            remixed_audio2, _ = apply_hpss(y2)
        elif remix_option == 'echo':
            remixed_audio1 = apply_echo(y1, sr1)
            remixed_audio2 = apply_echo(y2, sr2)
        else:
            # Apply all effects in sequence
            y1 = apply_echo(y1, sr1)
            y1, _ = apply_hpss(y1)
            remixed_audio1 = apply_pitch_shift(y1, sr1)

            y2 = apply_echo(y2, sr2)
            y2, _ = apply_hpss(y2)
            remixed_audio2 = apply_pitch_shift(y2, sr2)

        # Combine the processed audio (overlay both files)
        final_audio = np.add(remixed_audio1, remixed_audio2)

        # Export final audio as a .wav file
        final_audio_path = os.path.join('media', 'remixed_audio.wav')
        sf.write(final_audio_path, final_audio, sr1)

        with open(final_audio_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="audio/wav")
            response["Content-Disposition"] = 'attachment; filename="remixed_audio.wav"'
            return response

    return render(request, 'remix_audio_page.html')