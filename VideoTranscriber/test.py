import textwrap
from keybert import KeyBERT
from moviepy.editor import VideoFileClip  # To get video duration

import os
print(os.path.exists("temp_video.mp4"))

# ========== STEP 1: Initialize KeyBERT ==========
kw_model = KeyBERT()

def extract_topic_keybert(text):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=1)
    return keywords[0][0].title() if keywords else "General Topic"

# ========== STEP 2: Segment Transcript Using Real Duration ==========
def segment_transcript_text(transcript_text, total_video_duration, wrap_width=100):
    lines = textwrap.wrap(transcript_text, width=wrap_width)
    output = ""
    topic_tracker = {}
    topic_counter = 0

    # Dynamically divide video duration across all chunks
    duration_per_chunk = total_video_duration / len(lines) if lines else 0
    current_time = 0.0

    for line in lines:
        next_time = round(current_time + duration_per_chunk, 2)
        topic = extract_topic_keybert(line)

        if topic not in topic_tracker:
            topic_tracker[topic] = topic_counter
            output += f"\n=== Topic {topic_counter}: {topic} ===\n"
            topic_counter += 1

        output += f"[{current_time:.2f}s - {next_time:.2f}s] {line}\n"
        current_time = next_time

    return output.strip()

# ========== STEP 3: Get Video Duration ==========
def get_video_duration(video_path="temp_video.mp4"):
    clip = VideoFileClip(video_path)
    duration = clip.duration
    clip.close()
    return duration

# ========== STEP 4: Use Transcript + Real Video ==========
def process_transcript_with_video(transcript_text, video_path="temp_video.mp4"):
    print("Fetching video duration...")
    duration = get_video_duration(video_path)
    
    print("Segmenting transcript using KeyBERT with real timestamps...")
    return segment_transcript_text(transcript_text, duration)

# ========== Example Run ==========
transcript_text = """
supervised and unsupervised learning super is one which train the model with label there which are the model this is what the right opposite should be based on this learning is we just provide the data so why you want type of learning of the other what say you want to know the project which products are customers likely to buy based on the process history when supervised learning would be the better approach for example if you tell my also be able to protect 
"""

output = process_transcript_with_video(transcript_text, "temp_video.mp4")
print(output)
