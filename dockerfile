FROM ubuntu:24.04

# ---- System basics ----
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git curl build-essential python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    pip install --no-cache-dir uv==0.1.31

# ---- Copy code ----
WORKDIR /opt/gradio-pinokio
COPY . .

# ---- Install Python deps ----
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860
CMD ["python", "launcher.py", "--server-name", "0.0.0.0"]
