# 🏥 Medical Symptom Interpreter

[![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-API-FF6B6B?style=for-the-badge)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

## 🌟 Overview

Medical Symptom Interpreter is an AI-powered health assistant that helps users understand their symptoms and provides preliminary medical guidance. Built with Streamlit and powered by Groq's Llama 3.3 model, it offers voice and text input capabilities with comprehensive analysis including medicine suggestions and health recommendations.

### 🎯 Key Features

- 🎤 **Voice Input** - Speak your symptoms naturally using microphone or upload audio files
- 🤖 **AI-Powered Analysis** - Advanced medical interpretation using Groq's Llama 3.3 model
- 💊 **Medicine Suggestions** - OTC and prescription medication recommendations
- 📊 **Analytics Dashboard** - Track health patterns with interactive visualizations
- 📄 **PDF Reports** - Download comprehensive medical reports
- 📜 **History Tracking** - All consultations saved with patient names
- 📥 **CSV Export** - Download complete medical history for sharing with doctors
- 🌍 **Modern UI** - Clean, intuitive orange-themed interface

### 🚀 Live Demo

[View Live Demo](#) *(Add your deployed app link here)*

## 📋 Table of Contents

- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)
- [Disclaimer](#-disclaimer)

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| AI/ML | Groq API (Whisper + Llama 3.3) |
| Visualizations | Plotly |
| PDF Generation | ReportLab |
| Audio Processing | SoundDevice, SciPy |
| Data Processing | Pandas, NumPy |
| Language | Python 3.9+ |

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- Groq API Key ([Get it here](https://console.groq.com))
- Microphone (for voice recording)

### Step-by-Step Setup

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/medical-symptom-interpreter.git
cd medical-symptom-interpreter
