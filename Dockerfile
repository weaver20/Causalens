FROM python:3.11-slim

WORKDIR /app

# 1) Install build dependencies and graphviz dev headers
RUN apt-get update && apt-get install -y \
    build-essential \
    graphviz \
    libgraphviz-dev \
    pkg-config \
 && rm -rf /var/lib/apt/lists/*

# 2) Copy requirements.txt
COPY requirements.txt .

# 3) Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copy the rest of your code
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]