import os
import uuid
import streamlit as st
from elevenlabs import ElevenLabs, save, play
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Configure ElevenLabs
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Emotion-to-sound prompts
emotion_prompts = {
    "joy": "Upbeat percussive rhythm with light chimes and cheerful whistles, looping seamlessly",
    "sadness": "Soft ambient piano with gentle rain and distant thunder, slow and melancholic",
    "anger": "Heavy industrial drone with pulsating low-end hits and distorted static elements",
    "fear": "Tense atmospheric drone with high-pitched resonances and subtle heartbeats",
    "surprise": "Quick, sporadic digital stutters and rising synth pulses with sharp transitions",
    "calm": "Smooth ambient pad with slow ocean waves and warm synth swells, continuous and slow",
    "excitement": "Fast-paced electronic loop with clapping snares and rising arpeggios, high energy",
    "love": "Soft acoustic guitar loop with mellow background hums and harmonic textures",
    "anxiety": "Trembling synth drones with glitchy textures and irregular tapping patterns",
    "hope": "Gentle synth pad with a steady heartbeat kick and subtle chimes, uplifting and airy",
    "loneliness": "Minimal ambient loop with echoing footsteps and wind through an empty corridor",
    "confidence": "Bold bass rhythm with layered percussion and triumphant brass textures, cinematic",
    "curiosity": "Light percussive textures with plucked synths and mysterious pads, looping subtly",
    "despair": "Low rumbling drone with broken piano notes and distant metallic echoes",
    "nostalgia": "Faint vinyl crackles with warm synth chords and faded melodic fragments"
}

# Sentiment analysis
def analyze_sentiment(user_text: str) -> list:
    prompt = f"""Split this text into segments where the sentiment changes.
Output single-word sentiment tags for each segment (e.g., happy, tense, calm, anxious).
Join them with dots. No extra words.

Text: """{user_text}"""
"""
    response = model.generate_content(prompt)
    sentiments = response.text.strip().split('.')
    return [s.strip().lower() for s in sentiments if s.strip()]

# Function to play audio from ElevenLabs
def get_emotion_audio(emotion: str):
    if emotion not in emotion_prompts:
        st.warning(f"No sound prompt available for '{emotion}'.")
        return None
    try:
        audio = elevenlabs.text_to_sound_effects.convert(
            text=emotion_prompts[emotion],
            duration_seconds=6,
            prompt_influence=0.8
        )
        temp_filename = f"temp_{uuid.uuid4().hex}.mp3"
        save(audio, temp_filename)
        return temp_filename
    except Exception as e:
        st.error(f"Failed to generate sound: {e}")
        return None

# Streamlit UI
def main():
    st.title("🎧 Book Tunes with ElevenLabs")
    st.write("Enter a story or paragraph and get matching sound effects for each emotion in your text.")

    if 'sentiments' not in st.session_state:
        st.session_state.sentiments = []
        st.session_state.index = 0

    user_input = st.text_area("Enter your text here...", height=200)

    if st.button("Generate Emotions"):
        if not user_input.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("Analyzing sentiment..."):
                try:
                    sentiments = analyze_sentiment(user_input)
                    if sentiments:
                        st.session_state.sentiments = sentiments
                        st.session_state.index = 0
                        st.success(f"Detected sentiments: {' > '.join(sentiments)}")
                    else:
                        st.warning("No sentiments detected.")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

    if st.session_state.sentiments:
        current_emotion = st.session_state.sentiments[st.session_state.index]
        st.markdown(f"### Emotion: `{current_emotion}`")
        filepath = get_emotion_audio(current_emotion)
        if filepath:
            audio_html = f"""
            <audio autoplay loop controls>
                <source src="{filepath}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Previous") and st.session_state.index > 0:
                st.session_state.index -= 1
        with col2:
            if st.button("Next") and st.session_state.index < len(st.session_state.sentiments) - 1:
                st.session_state.index += 1

if __name__ == "__main__":
    main()
