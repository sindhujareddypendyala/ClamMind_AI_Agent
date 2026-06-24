# 🌿 CalmMind AI – Agentic Mental Wellness Companion

## 📖 Overview

CalmMind AI is an Agentic AI-powered Mental Wellness Companion designed to provide personalized emotional support, wellness guidance, mood insights, and interactive conversations.

The platform leverages a multi-agent architecture, conversation memory, mood analytics, wellness planning, voice interaction, and Groq-powered LLM responses to create a supportive and human-like mental wellness experience.

---

## ✨ Features

### 💬 AI Wellness Companion

* Natural conversational AI
* Personalized emotional support
* Context-aware responses
* Conversation memory

### 🧠 Multi-Agent Architecture

* Domain Guard Agent
* Emotion Detection Agent
* Memory Agent
* Therapist Agent
* Recommendation Agent
* Mood Prediction Agent
* Response Synthesis Agent

### 📈 Mood Tracker

* Automatic mood detection from conversations
* Mood history visualization
* Wellness score tracking
* Daily, weekly, and monthly mood trends

### 📋 Wellness Planner

* Personalized wellness plans
* Stress recovery plans
* Sleep improvement plans
* Confidence-building plans
* Burnout recovery plans

### 🧘 Wellness Exercises

* Guided breathing exercises
* Grounding exercises
* Relaxation techniques
* Mindfulness activities

### 🎤 Voice Assistant

* Voice recording
* Speech-to-text transcription
* AI-generated responses

### ⭐ Favorites

* Save helpful responses
* Save wellness exercises
* Quick access to important guidance

### 🕒 Chat History

* Conversation history
* Session management
* Personalized context retention

---

## 🏗️ System Architecture

```text
User
 ↓
Domain Guard Agent
 ↓
Emotion Detection Agent
 ↓
Memory Agent
 ↓
Mood Prediction Agent
 ↓
Recommendation Agent
 ↓
Therapist Agent
 ↓
Groq LLM (Llama 3.1)
 ↓
Response Synthesis
 ↓
Personalized Wellness Response
```

---

## 🛠️ Tech Stack

### Frontend

* React
* Tailwind CSS
* Framer Motion
* Axios

### Backend

* Python
* FastAPI

### AI & ML

* Groq API
* Llama 3.1
* Emotion Detection
* Recommendation Engine
* Agentic AI Workflow

### Database

* SQLite

### Other Tools

* Speech Recognition
* Text-to-Speech
* Chart Analytics

---

## 📂 Project Structure

```text
CalmMind_AI/

frontend/
│
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── App.jsx
│
└── package.json

backend/
│
├── agents/
├── services/
├── database/
├── prompts/
├── knowledge_base/
├── main.py
└── requirements.txt
```

---

### Installation


---

### Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

Run Backend:

```bash
uvicorn main:app --reload
```

---

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

## 🔑 Environment Variables

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

---

## 🎯 Key Objectives

* Promote emotional wellbeing
* Provide personalized wellness guidance
* Encourage self-reflection
* Deliver context-aware support
* Track emotional patterns over time

---

## 🔒 Disclaimer

CalmMind AI is designed for wellness support and self-reflection.

It is **not a substitute for professional medical advice, diagnosis, or treatment**.

If you are experiencing a mental health crisis, please seek help from a qualified healthcare professional or emergency service.

---

## 👩‍💻 Developer

**Sindhuja Reddy Pendyala**

B.Tech Data Science Student

Aspiring AI/ML Engineer

Built as part of a GenAI Internship Project.

---

## 🌟 Future Enhancements

* Advanced RAG-based wellness knowledge system
* Personalized AI Therapist
* Multi-language support
* Mobile application
* Advanced mood forecasting
* Community wellness features

---

