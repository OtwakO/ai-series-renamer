# Set the base image using Python 3.12 and Debian Bookworm
FROM python:3.12-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory to /app
WORKDIR /app

# Copy only the necessary files to the working directory
COPY ./app /app

# Install the requirements
# RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Run the app with the Litestar CLI
CMD ["python", "rename_series.py"]