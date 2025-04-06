import os
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tqdm import tqdm

dataset_path = "Sample_dataset" 
output_path = "processed_data"

os.makedirs(output_path, exist_ok=True)

def load_audio(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None)
        return y, sr
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None, None
    
def audio_to_spectrogram(y, n_fft=2048, hop_length=512):

    S = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)
    return S_db

def preprocess_audio(folder_path, output_path):
    spectrograms = []
    labels = []
    
    for music_folder in tqdm(os.listdir(folder_path), desc="Processing Dataset"):
        music_path = os.path.join(folder_path, music_folder)
        if not os.path.isdir(music_path):
            continue  
        for component in ["mixture", "vocals", "drums", "bass", "other"]:
            component_path = os.path.join(music_path, f"{component}.wav")
            if os.path.exists(component_path):
                y, sr = load_audio(component_path)
                if y is None:
                    continue
                
                S_db = audio_to_spectrogram(y)
                output_file = os.path.join(output_path, f"{music_folder}_{component}.npy")
                np.save(output_file, S_db)
                
                spectrograms.append(S_db)
                labels.append(component)
            else:
                print(f"{component_path} does not exist.")
    
    return spectrograms, labels


def visualize_spectrogram(S_db, title="Spectrogram"):
    """Visualize a single spectrogram."""
    plt.figure(figsize=(10, 6))
    librosa.display.specshow(S_db, sr=22050, x_axis='time', y_axis='log', cmap='viridis')
    plt.colorbar(format="%+2.0f dB")
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Frequency")
    plt.show()


def visualize_label_distribution(data_info):
    """Visualize the distribution of audio components."""
    plt.figure(figsize=(8, 6))
    sns.countplot(data=data_info, x="Label", palette="pastel")
    plt.title("Distribution of Audio Components")
    plt.xlabel("Audio Component")
    plt.ylabel("Count")
    plt.show()

def visualize_spectrogram_shapes(data_info):
    """Visualize the distribution of spectrogram shapes."""
    plt.figure(figsize=(10, 6))
    shape_counts = data_info["Spectrogram Shape"].value_counts()
    shape_counts.plot(kind='bar', color='skyblue')
    plt.title("Spectrogram Shape Distribution")
    plt.xlabel("Shape")
    plt.ylabel("Count")
    plt.show()

def analyze_dataset(data_info, spectrograms, labels):
    """Perform dataset analysis and visualization."""
    visualize_label_distribution(data_info)
    visualize_spectrogram_shapes(data_info)


def main():
    DATASET_PATH = "Sample_dataset" 
    OUTPUT_PATH = "processed_data"
    print("Starting preprocessing...")
    spectrograms, labels = preprocess_audio(DATASET_PATH, OUTPUT_PATH)
    
    data_info = pd.DataFrame({
        "Spectrogram Shape": [s.shape for s in spectrograms],
        "Label": labels
    })
    
    data_info.to_csv(os.path.join(OUTPUT_PATH, "dataset_analysis.csv"), index=False)
    print("Preprocessing complete. Analysis data saved.")
    
    print("Starting analysis and visualization...")
    for i, (spec, label) in enumerate(zip(spectrograms[:5], labels[:5])):
        visualize_spectrogram(spec, title=f"Spectrogram ({label})")
    
    analyze_dataset(data_info, spectrograms, labels)
    print("Analysis and visualization complete.")


main()