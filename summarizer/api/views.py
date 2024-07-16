import whisper
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from .models import Video
from .serializers import VideoSerializer
import speech_recognition as sr
import os
import openai

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    openai.api_key = 'my open AI key was present here actually before, while uploading to github I deleted that'
    def get_openai_response(self,prompt):
        response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        temperature=0.5,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
        
        return (response['choices'][0]['text'])

    def extract_audio_from_video(self, video_file, audio_file):
        video = VideoFileClip(video_file)
        video.audio.write_audiofile(audio_file)

    def convert_audio_to_text(self, audio_file):
        recognizer = sr.Recognizer()
        audio = AudioSegment.from_file(audio_file)
        audio.export("temp.wav", format="wav")

        with sr.AudioFile("temp.wav") as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        return text

    
    

    def perform_create(self, serializer):
        video = serializer.save()
        file_path = video.file.path
        file_extension = os.path.splitext(file_path)[1].lower()
        transcribed_text = ""

        if file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
           
            audio_path = file_path.replace(file_extension, ".wav")
            self.extract_audio_from_video(file_path, audio_path)
            transcribed_text = self.convert_audio_to_text(audio_path)
        elif file_extension in ['.wav', '.mp3', '.m4a']:
            
            transcribed_text = self.convert_audio_to_text(file_path)
        else:
            raise ValueError("Unsupported file type")

        
        prompt = f'Summarize this text in one line: {transcribed_text}'
        summarized_text = self.get_openai_response(prompt)


        video.transcription = transcribed_text
        video.summary = summarized_text
        video.save()

    @action(detail=True, methods=['get'])
    def transcription(self, request, pk=None):
        video = self.get_object()
        return Response({'transcription': video.transcription, 'summary': video.summary})
