# Gunakan image Python ringan
FROM python:3.10-slim

# Set direktori kerja di dalam kontainer
WORKDIR /app

# Install dependency sistem (opsional tapi sering dibutuhkan oleh OpenCV)
RUN apt-get update && apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file proyek
COPY . .

# Set environment variables
ENV FLASK_APP=Backend/Backend.py
ENV FLASK_ENV=production

# Hugging Face Spaces secara default mengekspos port 7860
EXPOSE 7860

# Jalankan server menggunakan Gunicorn (Standar Production)
CMD ["gunicorn", "-b", "0.0.0.0:7860", "Backend.Backend:app"]
