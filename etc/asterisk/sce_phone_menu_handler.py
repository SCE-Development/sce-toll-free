#!/usr/bin/env python3
from datetime import datetime
import json
import os
import subprocess
import sys
import tempfile

import pytz
from gtts import gTTS  # or remove if using espeak

SOUNDS_DIR = "/var/lib/asterisk/sounds"


def encode_wav_as_phone_quality(input_path, output_path):
    return subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", "8000",
        "-ac", "1",
        "-acodec", "pcm_s16le",
        output_path
    ], 
        stdout=subprocess.DEVNULL,  # discard stdout
        stderr=subprocess.DEVNULL,  # discard stderr
          check=True)

def combine_audio_and_encode_output_as_phone_quality(files, output_path):
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as f:
        for path in files:
            f.write(f"file '{path}'\n")
        f.flush()
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", f.name,
            "-ar", "8000", "-ac", "1", "-acodec", "pcm_s16le",
            output_path
        ], 
        stdout=subprocess.DEVNULL,  # discard stdout
        stderr=subprocess.DEVNULL,  # discard stderr
        check=True)

def main():
    import random
    if sys.argv[1] == 'phone_stats':
        pacific = pytz.timezone("America/Los_Angeles")
        now = datetime.now(pacific)
        time_str = now.strftime("%I:%M %p %Z").lstrip("0")
        tts = gTTS(text=time_str, lang='en')
        tts.save('/var/lib/asterisk/sounds/time.wav')
        tts = gTTS(text=str(random.randint(1,100)), lang='en')
        tts.save('/var/lib/asterisk/sounds/number.wav')

        encode_wav_as_phone_quality('/var/lib/asterisk/sounds/time.wav', '/var/lib/asterisk/sounds/time_tmp.wav')
        encode_wav_as_phone_quality('/var/lib/asterisk/sounds/number.wav', '/var/lib/asterisk/sounds/number_tmp.wav')

        os.rename('/var/lib/asterisk/sounds/time_tmp.wav', '/var/lib/asterisk/sounds/time.wav')
        os.rename('/var/lib/asterisk/sounds/number_tmp.wav', '/var/lib/asterisk/sounds/number.wav')

        combine_audio_and_encode_output_as_phone_quality(
            [
                '/etc/asterisk/favorite_number/as_of.wav',
                '/var/lib/asterisk/sounds/time.wav',
                '/etc/asterisk/favorite_number/my_favorite_number_is.wav',
                '/var/lib/asterisk/sounds/number.wav',
            ],
            '/var/lib/asterisk/sounds/phone_stats.wav',
        )


    if sys.argv[1] == 'leetcode':
        # i dont feel like installing requests
        subprocess.run([
            "curl", "localhost:8000/phone",
            "-o", "/var/lib/asterisk/sounds/leetcode.wav"
        ], check=True)
    
    if sys.argv[1] == 'status':
        result = subprocess.run([
            "curl", "--insecure", "https://sce.sjsu.edu/status/?json"
        ], capture_output=True, text=True, 
        
        check=True)

        try:
            # result.stdout now contains the JSON as a string
            json_data = json.loads(result.stdout)
            """
            Collect jobs whose last value is not "1"
            the JSON response looks like
            [
                {
                    "instance": "server:8001",
                    "job": "sceta-server",
                    "is_up": true,
                    "values": [
                        {
                            "timestamp": "2025-11-06 05:48:09",
                            "value": "1"
                        }
                    ]
                }
            ]
            """
            jobs_not_ok = []
            for entry in json_data:
                if entry.get("values"):
                    last_value = entry["values"][-1]["value"]
                    if last_value != "1":
                        jobs_not_ok.append(entry["job"])
            if not jobs_not_ok:
                os.remove('/var/lib/asterisk/sounds/ongoing_outage.wav')
                print("no")
                return
            def join_with_and(lst):
                if not lst:
                    return ""
                elif len(lst) == 1:
                    return lst[0]
                elif len(lst) == 2:
                    return f"{lst[0]} and {lst[1]}"
                else:
                    return f"{', '.join(lst[:-1])} and {lst[-1]}"
            tts = gTTS(text=join_with_and(jobs_not_ok), lang='en')
            tts.save('/var/lib/asterisk/sounds/impacted_services.wav')
            encode_wav_as_phone_quality('/var/lib/asterisk/sounds/impacted_services.wav', '/var/lib/asterisk/sounds/impacted_services_tmp.wav')
            os.rename('/var/lib/asterisk/sounds/impacted_services_tmp.wav', '/var/lib/asterisk/sounds/impacted_services.wav')
            combine_audio_and_encode_output_as_phone_quality(
                [
                    '/var/lib/asterisk/sounds/we_are_currently.wav',
                    '/var/lib/asterisk/sounds/impacted_services.wav',
                    '/var/lib/asterisk/sounds/we_will_fix_it.wav',
                ],
                '/var/lib/asterisk/sounds/ongoing_outage.wav',
            )
            print("yes")


        except Exception:
            os.remove('/var/lib/asterisk/sounds/ongoing_outage.wav')
            print("no")

        

if __name__ == "__main__":
    main()


