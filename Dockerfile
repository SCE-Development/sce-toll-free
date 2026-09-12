FROM mlan/asterisk

RUN apk add --no-cache python3 py3-pip ffmpeg vim

RUN python3 -m pip install --no-cache-dir \
    requests \
    pytz \
    gTTS --break-system-packages
