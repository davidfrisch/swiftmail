
# AI Query-Response System

This repository contains the source code for the AI Query-Response system developed for the MSc research project titled **"Requirements, Design, and Evaluation of an AI-based Query-Response System"**. It includes the system's core functionality and the evaluation methods used in the research.

## Installation

### Prerequisites

Ensure the following software is installed on your machine:

- [Ollama](https://ollama.com/download)
- [Docker](https://docs.docker.com/get-docker/)

### Starting the AnythingLLM Server

[AnythingLLM](https://anythingllm.com) is a platform for deploying and interacting with large language models. It allows you to add documents, train models, and query the models via an API. To start the server, run the following command in your terminal:

```bash
docker compose up
```

### Frontend Setup

The frontend is a React application. To set it up:

1. Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2. Install the necessary dependencies:
    ```bash
    npm install
    ```
3. Start the development server:
    ```bash
    npm run dev
    ```

### Backend Setup

The backend is a Python Flask application. To set it up:

1. Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2. Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Start the backend server:
    ```bash
    python main.py
    ```
