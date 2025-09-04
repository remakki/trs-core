# TRS-SERVICE
TRS is a service for finding news stories from streams, storing and analyzing them. TRS-core is the main service that identifies news stories from the stream, makes a short summary using AI, and notifies about new stories.


## Getting started
Follow the steps below to set up and run the speech-service using Docker.

### 📦 Install Dependencies

#### Using `uv`:
```bash
uv sync
```
   
### ⚙️ Configure Environment Variables

Copy the example environment file and fill in the necessary values:

```bash
cp .env.example .env
```

Edit the `.env` file to set your environment variables. You can use the default values or customize them as needed.

### 🐳 Build and Run the Docker Container

Build the Docker image:

```bash
docker build -t trs-core .
```

Run the container with environment variables from .env:

```bash
docker run -d -env-file .env --name trs-core trs-core
```

This will build the Docker image and start the container with environment variables from the .env file.
