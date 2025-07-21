import speech_recognition as sr
import language_tool_python
import re
import os

def transcribe_audio():
    recognizer = sr.Recognizer()
    mic_index = 0  
    with sr.Microphone(device_index=mic_index) as source:
        print("Adjusting for background noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        print("Speak a paragraph clearly...")
        audio = recognizer.listen(source, timeout=5)
    
    try:
        return recognizer.recognize_google(audio)  
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "API error or no internet connection"

def transcribe_audio_file(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        print("Processing audio file...")
        audio = recognizer.record(source)
    
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "API error or no internet connection"


def fix_text_formatting(text):
    text = text.strip()
    text = text[0].upper() + text[1:] if text else ""
    if text and text[-1] not in ".!?":
        text += "."
    return text


def analyze_text(text):
    tool = language_tool_python.LanguageTool('en-US')
    grammar_errors = tool.check(text)
    num_errors = len(grammar_errors)
    total_words = len(text.split())
    
    
    if total_words == 0:
        accuracy_score = 0
    else:
        error_penalty = (num_errors / total_words) * 100
        accuracy_score = max(0, 100 - error_penalty)  
    
    return grammar_errors, accuracy_score

# Main 
if __name__ == "__main__":
    choice = input("Choose input method: (1) Microphone (2) Upload Audio File: ")
    
    if choice == "1":
        print("Press Enter to start recording...")
        input()
        transcribed_text = transcribe_audio()
    elif choice == "2":
        file_path = input("Enter the path of the audio file: ")
        if not os.path.exists(file_path):
            print("File not found. Please check the path and try again.")
            exit()
        transcribed_text = transcribe_audio_file(file_path)
    else:
        print("Invalid choice. Exiting...")
        exit()
    
    print("\nOriginal Transcription (Raw):")
    print(transcribed_text)

    if "Could not understand audio" in transcribed_text or "API error" in transcribed_text:
        print("Please try again with a clearer voice.")
    else:
        formatted_text = fix_text_formatting(transcribed_text)

        print("\nFormatted Transcription (With Capitalization & Punctuation):")
        print(formatted_text)

        grammar_mistakes, accuracy_score = analyze_text(formatted_text)
        num_errors = len(grammar_mistakes)

        print(f"\nGrammar Mistakes: {num_errors}")
        if num_errors > 0:
            print("\nDetailed Grammar Mistakes:")
            for mistake in grammar_mistakes:
                print(f"- Incorrect: {mistake.context}")
                print(f"  Suggestion: {', '.join(mistake.replacements)}\n")

        print(f"Final Accuracy Score: {accuracy_score:.2f}%")
