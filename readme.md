# 🏋️‍♂️ GYM-CHAT

**GYM-CHAT** is a conversational assistant focused on gym and fitness topics. This personal project combines Natural Language Processing (NLP) with a real-time web interface, allowing users to interact with an intelligent system capable of understanding questions and delivering helpful responses about exercises, muscles, and workout routines — all through a dynamic chat interface.

---

## 📌 Project Goals

- Provide a conversational interface focused on physical training and fitness.
- Understand and classify user messages using NLP with spaCy.
- Respond with information based on structured resources about muscles and exercises.
- Display the results through a responsive and real-time chat interface.

---

## 🧠 How It Works

The system is divided into three main components:

### 1. **Frontend** (`app/frontend/`)
The web interface built with **Flask** and **Socket.IO**, enabling real-time chat communication. It uses HTML, CSS, and JavaScript.

- 📄 `index.html`: Main chat UI template.
- 🖼️ `static/`: Contains styles, JavaScript scripts, and images.

### 2. **Backend** (`app/backend/`)
Contains the core logic for processing user input and returning meaningful responses:

#### a. `core/analyzer.py`
- Uses **spaCy** with the **`es_core_news_sm`** Spanish model to process text input.
- Extracts named entities like exercises, muscle groups, and body parts.
- Classifies message intent using semantic rules.
- Relies on the `entities_spacy.json` resource for entity mapping.

#### b. `data/loader.py`
- Loads structured data from `exercises.json` and `muscles.json`.
- Performs data lookups based on the analysis to return relevant responses.
- Provides exercise descriptions, recommendations, or filtered lists.

### 3. **Main Server** (`app/main.py`)
- Main entry point of the app.
- Runs a **Flask** server with **Flask-SocketIO** for real-time interaction.
- Integrates the Analyzer and Loader modules to process chat messages and return live responses.

---

## 📂 Project Structure
```bash
GYM-CHAT/
├── backend/
│   ├── app.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── analyzer.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── loader.py
│   └── resources/
│       ├── entities_spacy.json
│       ├── exercises.json
│       └── muscles.json
├── frontend/
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── script.js
├── .gitignore
├── LICENSE
├── readme.md
└── requirements.txt


```
---

## ▶️ How to Run the Project

### Live Demo

You can check out the app live here:  
🔗 [https://gym-chat.onrender.com/](https://gym-chat.onrender.com/)

### 1. Clone the repository
```bash
git clone https://github.com/dfedezqui/GYM-CHAT
cd GYM-CHAT
```
### 2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install the Spanish NLP model (spaCy)
This project uses the spaCy Spanish model es_core_news_sm. It must be downloaded manually:
```bash
python -m spacy download es_core_news_sm
```
Alternatively, you can include this in your code to handle it automatically:
```python
import spacy

try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    raise OSError("The spaCy model 'es_core_news_sm' is not installed. Run:\npython -m spacy download es_core_news_sm")
```

### 5. Run the application
```bash
python backend/app.py
```
The server will be available by default at:
👉 http://localhost:5000

## 🧰 Technologies Used
### Python 3.10+

### Flask

### Flask-SocketIO

### spaCy

### HTML/CSS/JavaScript

### JSON (as the knowledge base)

## ✍️ Author
Developed by [Fernández Quiñones, David] as a personal project to demonstrate skills in Natural Language Processing, real-time web development, and modular backend architecture.

## 📄 License

This project is licensed under the MIT License.  
See the [LICENSE](./LICENSE) file for more details.
