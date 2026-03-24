# Integrated Academic Management & Examination System (EduNexus)

EduNexus is a multi-service Academic Management and Examination System that integrates student management, examination processes, real-time chat and notifications, and financial operations into a centralized platform. The system is built using Django, Django REST Framework, WebSockets for real-time chat, Celery, Redis, Docker, and PayPal integration to simulate a production-level environment.

##  System Architecture
The project is architected into four distinct applications, all containerized with **Docker** to ensure environment consistency and scalable deployment.

---

## Project Modules

### 1. Teacher & Examination Module
* **Workflow:** Secure Auth $\rightarrow$ Create Assignment $\rightarrow$ Add Questions $\rightarrow$ Publish.
* **Automation:** On publication, a notification trigger is sent to all registered students.
* **Analytics Dashboard:** Teachers can track performance metrics, including Pass/Fail ratios and class averages.
* **Automated Reporting:** Once a deadline passes, the system compiles a summary report and emails it to the teacher.

### 2. Student Portal Module
* **Assessment:** Interactive UI for attempting published tests.
* **Instant Feedback:** Upon submission, the system calculates scores using an automated grading logic.
* **Mail Service:** Sends a detailed result breakdown to the student's email immediately after test completion.

### 3. Professional Chat App
* **One-to-One (LinkedIn-style):** Private, secure messaging between teachers and students.
* **Group Chat (WhatsApp-style):** Real-time departmental or class-based group rooms.
* **Technology:** Driven by WebSockets for low-latency communication and message history.

### 4. HR & Payroll App
* **Data Integration:** Automatically pulls attendance and performance data to generate monthly payroll.
* **One-Click Payment:** A dedicated HR interface to trigger salary disbursements to teacher accounts.
* **Financial Tracking:** A comprehensive dashboard to monitor paid vs. pending salaries and historical expenditure.

---

##  Tech Stack & DevOps
* **Backend:** Python (Django / Django REST Framework)
* **Asynchronous Tasks:** Celery & Redis (for Emailing and Payroll processing)
* **Real-time:** WebSockets (Django Channels)
* **Database:** PostgreSQL
* **Containerization:** Docker & Docker Compose
* **Payments:** Integration with Payouts API

---

##  Getting Started (Docker)

To run the entire ecosystem locally, ensure you have **Docker** and **Docker Compose** installed:

## Clone the Project

```bash
# Clone the repository
git clone https://github.com/Divakar-009/Academic-Management-and-Examination-System.git

# Go into project directory
cd Academic-Management-and-Examination-System

- Download Docker and use this command to run project **Docker Compose**, 
```bash
docker-compose up --build
