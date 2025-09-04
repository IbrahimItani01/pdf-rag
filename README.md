# 📄 DocChat

DocChat is a **PDF Retrieval-Augmented Generation (RAG) application** that lets you interact with PDF documents conversationally.  
Instead of manually searching through lengthy PDFs, you can simply ask a question and get context-aware, accurate answers.  

---

## 🚀 Features
- Upload and process PDF documents  
- Smart text chunking with **LangChain**  
- Semantic search using **Pinecone** vector database  
- Context-aware responses powered by **OpenAI**  
- REST API built with **FastAPI**  

---

## 🛠️ Tech Stack
- **Backend:** FastAPI  
- **Vector Database:** Pinecone  
- **AI/LLM:** OpenAI  
- **Orchestration:** LangChain  
- **Embeddings:** OpenAI Embeddings  

---

## 📂 Project Structure
```bash
docchat/
├── src/
│   ├── middlewares/     
│   ├── models/          # The request/response models
│   ├── routes/          # The routes of all apis
│   ├── services/        # The business logic of all apis
│   └── shared/          # The util functions and constants used accross codebase
├── requirements.txt
├── README.md
├── app.py              # Entry point
└── .env.example
```
## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/IbrahimItani01/pdf-rag.git
cd pdf-rag

python -m venv venv
# Activate the environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 2. Set up environment variables
Create a `.env` file in the root directory base on the `.env.example` file

### 3. Run the application
```bash
fastapi dev app.py
```

---

If you have any inquiries feel free to reach out on `ib.itani01@gmail.com`