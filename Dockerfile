FROM python:3.10-slim

# set working directory
WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000 8501

# Start both FastAPI and Streamlit
CMD ["bash", "-c", \
     "uvicorn app.main_api:app --host 0.0.0.0 --port 8000 & \
      streamlit run app/streamlit_gui.py --server.port 8501 --server.address 0.0.0.0"]