# 1. Base image (Switching to Debian-based slim image for stability)
FROM python:3.11-slim

# Set environment variables (using modern syntax to avoid warnings)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# --- 2. Install System Dependencies and Tools (as root) ---
# Use 'apt' instead of 'apk' for Debian/Slim images.
# Install build essentials, X11 libraries, and the full Qt6 development suite.
RUN apt update && \
    apt install -y --no-install-recommends \
        # Build Essentials (CRITICAL for compiling NumPy, OpenCV, PyQt6)
        build-essential \
        # GUI and X11 Libraries (RUNTIME)
        libxext6 libxrender1 libxtst6 \
        # Video/Media Libraries
        libavformat-dev libavcodec-dev libavutil-dev \
        # Qt Development Libraries (REQUIRED for PyQt6, tools, and plugins)
        qt6-base-dev \
        qt6-tools-dev \
        qt6-declarative-dev \
        qt6-svg-dev \
        # Desired CLI tools
        bash nano \
    && rm -rf /var/lib/apt/lists/*

# --- 3. Application Setup and Security ---

# Create the main working directory
WORKDIR /app

# Copy dependency list and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- 4. Non-Root User Security Setup (Critical) ---
# Create a dedicated non-root user (using Debian's 'adduser' default)
RUN adduser --disabled-password --gecos "" mirauser

# Copy the entire 'src' directory and main entry point
COPY src/ /app/src/

# Change ownership of the app directory to the new user
RUN chown -R mirauser:mirauser /app

# Switch the user context. All commands below run as 'mirauser'.
USER mirauser

# --- 5. Define Entry Point ---
CMD ["python", "/app/src/main.py"]