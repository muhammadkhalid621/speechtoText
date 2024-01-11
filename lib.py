import tkinter as tk
import threading
import pyaudio
import wave
from tkinter import *
import tkinter.font as font
from tkinter.filedialog import asksaveasfilename
from tkinter import filedialog
import os
import soundfile as sf
from pydub import AudioSegment

import speech_recognition as sr




class App():
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 2
    fs = 44100

    frames = []

    

    def __init__(self, master):
       
        self.isrecording = False
        myFont = font.Font(weight="bold")

        # Heading
        self.heading_label = tk.Label(main, text="Hebrew Speech to Text", font=("Helvetica", 24, "bold"))
        self.heading_label.pack(pady=10)

        self.heading_label = tk.Label(main, text="(Can Record or upload voice)", font=("Arial", 14, "bold"))
        self.heading_label.pack(pady=10)

        self.button1 = tk.Button(main, text='Record', command=self.startrecording,
                                 height=2, width=20, bg='#0052cc', fg='#ffffff')
        self.button2 = tk.Button(main, text='stop', command=self.stoprecording,
                                 height=2, width=20, bg='#0052cc', fg='#ffffff', state=tk.DISABLED)
        self.button3 = tk.Button(main, text='Upload File', command=self.open_audio,
                                 height=2, width=20, bg='#0052cc', fg='#ffffff')
        self.button1['font'] = myFont
        self.button2['font'] = myFont
        self.button3['font'] = myFont

        self.button1.pack(pady=10)
        self.button2.pack(pady=10)
        self.button3.pack(pady=10)

        # Loading Indicators
        self.loading_recording_label = tk.Label(main, text="Recording...", font=("Helvetica", 12), fg="red")
        self.loading_converting_label = tk.Label(main, text="Converting to Text...", font=("Helvetica", 12), fg="red")

        self.is_recording = tk.BooleanVar()
        self.is_recording.set(False)

        # List to store the recognized text of each segment
        self.segment_texts = []

    def start_recording(self):

        myFont = font.Font(weight="bold")
        print('recording start')

        

    def startrecording(self):
        self.button2.config(state=tk.NORMAL)
        self.button1.config(state=tk.DISABLED)
        self.button3.config(state=tk.DISABLED)

        # Show loading indicator for recording
        self.loading_recording_label.pack()

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.sample_format, channels=self.channels,
            rate=self.fs, frames_per_buffer=self.chunk, input=True)
        self.isrecording = True

        print('Recording')
        t = threading.Thread(target=self.record)
        t.start()

        

    def stoprecording(self):
        self.loading_recording_label.pack_forget()

        self.isrecording = False
        print('recording complete')


        self.filename = asksaveasfilename(initialdir="/", title="Save Audio File",
            filetypes=(("audio file", "*.wav"), ("all files", "*.*")),
            defaultextension=".wav")
        
        print(self.filename)

        # Show loading indicator for converting audio to text
        self.loading_converting_label.pack()

        wf = wave.open(self.filename, 'wb')
        self.start_recording()
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))

        self.check_voice(self.filename, segment_duration=10)

        # Concatenate the recognized text of all segments
        final_text = " ".join(self.segment_texts)
        print(f"Final Recognized Text: {final_text}")

        text_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], title="Save Text File")
        with open(text_file_path, "w") as text_file:
            text_file.write(final_text)

        print(f"Final recognized text saved to: {text_file_path}")

        # Hide loading indicator for converting audio to text
        self.loading_converting_label.pack_forget()

        # Clear the list for the next recording session
        self.segment_texts = []

        self.button1.config(state=tk.NORMAL)
        self.button2.config(state=tk.DISABLED)
        self.button3.config(state=tk.NORMAL)


    def open_audio(self):
        self.button1.config(state=tk.DISABLED)
        self.button2.config(state=tk.DISABLED)
        self.button3.config(state=tk.DISABLED)
        self.start_recording()
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav")])
        print(file_path)

        self.loading_converting_label.pack()

        self.check_voice(file_path, segment_duration=10)

        # Concatenate the recognized text of all segments
        final_text = " ".join(self.segment_texts)
        print(f"Final Recognized Text: {final_text}")

        text_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], title="Save Text File")
        with open(text_file_path, "w") as text_file:
            text_file.write(final_text)

        print(f"Final recognized text saved to: {text_file_path}")

        # Hide loading indicator for converting audio to text
        self.loading_converting_label.pack_forget()

        # Clear the list for the next recording session
        self.segment_texts = []

        self.button1.config(state=tk.NORMAL)
        self.button2.config(state=tk.NORMAL)
        self.button3.config(state=tk.NORMAL)

    

    def record(self):
        while self.isrecording:
            data = self.stream.read(self.chunk)
            self.frames.append(data)
            print("does it")




    def check_voice(self, audio_path, segment_duration=10):
        print(audio_path)
        audio = AudioSegment.from_wav(audio_path)

        total_duration = len(audio)

        # Calculate the number of segments
        num_segments = int(total_duration / (segment_duration * 1000)) + 1

        

        for i in range(num_segments):
            start_time = i * segment_duration * 1000
            end_time = min((i + 1) * segment_duration * 1000, total_duration)

            # Extract the audio segment
            audio_segment = audio[start_time:end_time]

            # Save the audio segment to a temporary file
            segment_path = f"segment_{i + 1}.wav"
            audio_segment.export(segment_path, format="wav")

            # Recognize the speech in the segment
            recognizer = sr.Recognizer()

            with sr.AudioFile(segment_path) as source:
                audio_data = recognizer.record(source)

            try:
                segment_text = recognizer.recognize_google(audio_data, language="he-IL")
                # Append the recognized text to the list
                self.segment_texts.append(segment_text)
                print(segment_text)
            except sr.UnknownValueError as e:
                print(e)
                print("Speech Recognition could not understand audio")
                continue
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                continue

            # Optionally, you can remove the temporary file after processing
            os.remove(segment_path)





main = tk.Tk()
main.title('Speech to Text')
main.geometry('820x440')
app = App(main)
main.mainloop()
