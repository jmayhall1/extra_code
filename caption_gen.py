# coding=utf-8
import whisper

model = whisper.load_model("base")  # options: tiny, base, small, medium, large

result = model.transcribe("C:/Users/jmayhall/Downloads/Lab7.mp4")

# Save as SRT captions
with open("captions.srt", "w") as f:
    for i, segment in enumerate(result["segments"]):
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]

        def format_time(seconds):
            hrs = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds - int(seconds)) * 1000)
            return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

        f.write(f"{i+1}\n")
        f.write(f"{format_time(start)} --> {format_time(end)}\n")
        f.write(f"{text.strip()}\n\n")