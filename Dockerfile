# ------------------------
# BASE IMAGE
# ------------------------
FROM python:3.10-slim

# ------------------------
# SET WORKING DIRECTORY
# ------------------------
WORKDIR /app

# ------------------------
# COPY FILES
# ------------------------
COPY . .

# ------------------------
# INSTALL DEPENDENCIES
# ------------------------
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    requests \
    python-dotenv \
    openai \
    openenv-core

# ------------------------
# EXPOSE PORT
# ------------------------
EXPOSE 7860

# ------------------------
# RUN SERVER
# ------------------------
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]