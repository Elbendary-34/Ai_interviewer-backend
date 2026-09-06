# intervyou_backend

## 1. Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Git

---

## 2. Local Environment Setup

**Clone the repository:**

```bash
git clone <repository-url>
cd intervyou_backend
```

**Create a virtual environment:**

```bash
python -m venv venv
```

**Activate the virtual environment:**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Set up environment variables:**

```bash
cp .env.example .env
```

---

## 3. Running Infrastructure

Start PostgreSQL, Redis, and LiveKit in the background:

```bash
docker-compose up -d
```

---

## 4. Database Migration

Apply all pending migrations:

```bash
alembic upgrade head
```

---

## 5. Running the Application

Start the FastAPI development server with hot reload:

```bash
uvicorn app.main:app --reload
```

---

## 6. Git & PR Workflow

Every developer must follow this workflow for every task:

1. **Pull the latest changes from `main`:**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create a new branch for your task:**
   ```bash
   git checkout -b feat/task-name
   ```
   or
   ```bash
   git checkout -b fix/issue-name
   ```

3. **Write your code and ensure it's properly formatted** before committing.

4. **Commit and push your branch:**
   ```bash
   git add .
   git commit -m "feat: description of the change"
   git push origin feat/task-name
   ```

5. **Open a Pull Request (PR)** targeting the `main` branch.

> ⚠️ **Strict Rule:** Direct pushes to `main` are **not allowed** under any circumstance. Every change must go through a Pull Request and be reviewed and approved by the Team Lead before merging.