# Patient 360 Summary App

An AI-powered healthcare data summarization platform that aggregates
patient records and generates a structured 360° summary using FastAPI,
React, and an LLM (Ollama or OpenAI).

------------------------------------------------------------------------

## Tech Stack

### Frontend

-   React (Vite)
-   Axios
-   LocalForage

### Backend

-   Python 3.9+
-   FastAPI
-   Uvicorn
-   Pydantic

### AI Layer

-   Ollama (Llama3) OR OpenAI API

------------------------------------------------------------------------

# Run Backend Locally

## 1️⃣ Clone the repository

``` bash
git clone https://github.com/gayathridevipappu/patient_summary_360.git
cd patient-summary-360/backend
```

## 2️⃣ Create virtual environment

``` bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

## 3️⃣ Install dependencies

``` bash
pip install fastapi uvicorn pydantic python-multipart requests
```

------------------------------------------------------------------------

## 4️⃣ Setup LLM

Install Ollama:

``` bash
brew install ollama        # Mac
```

Pull llama3 model:

``` bash
ollama pull llama3
```

Start Ollama:

``` bash
ollama run llama3
```

Keep Ollama running in background.

------------------------------------------------------------------------

## 5️⃣ Start Backend Server

``` bash
uvicorn main:app --reload
```

Backend will run at:

    http://127.0.0.1:8000

------------------------------------------------------------------------
