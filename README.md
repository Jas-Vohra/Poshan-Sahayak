# Poshan Sahayak: AI-Driven Rural Healthcare & Resource Management

**Poshan Sahayak** (Nutrition Assistant) is a Python-based ecosystem developed to digitize and optimize critical healthcare workflows in resource-constrained environments. Originally designed for **Anganwadi centers**, the system's logic has been extended to manage **Blood Bank inventories**, ensuring that life-saving resources are tracked and allocated efficiently.

## 📌 The Problem
In rural India, Anganwadi workers and local health centers often rely on manual paper registers to track child growth, vaccination schedules, and inventory. This leads to:
* **Delayed Intervention**: Malnutrition is often identified too late.
* **Information Asymmetry**: Parents are not always aware of upcoming vaccination dates.
* **Resource Leakage**: Inefficient tracking of ration and medical supplies like blood units.

## 🚀 The Solution: A Dual-Purpose Assistant
Poshan Sahayak uses a centralized Python backend to automate data entry and provide proactive alerts via Telegram and WhatsApp.

### 1. Anganwadi Integration
* **Smart Growth Monitoring**: Uses age-to-weight algorithms to instantly flag "Severe Malnutrition" cases.
* **Automated Outreach**: Sends automated WhatsApp alerts to parents for due vaccinations (BCG, Pentavalent, etc.).
* **Hindi Voice Interface**: Utilizes gTTS (Google Text-to-Speech) to provide audio feedback in the local language for workers with varying literacy levels.

### 2. Blood Bank Management
* **Real-Time Inventory**: Track blood groups (A+, B-, etc.) and units available.
* **Donor Database**: A searchable directory to quickly contact eligible donors during emergencies.
* **Audit Trail**: Generates digital logs for every unit added or distributed to ensure transparency.

## 🛠️ Technical Implementation
* **Backend**: Python 3.x
* **Framework**: `python-telegram-bot` for the user interface.
* **Data Persistence**: CSV-based secure logging for offline-capable data management.
* **Visualization**: `Matplotlib` for generating dynamic child growth charts.
* **Messaging**: Twilio API integration for real-time WhatsApp health alerts.

## 🌟 Recognition
* **National Finalist**: Youth Ideathon (Top 125 in India)
* **Capstone Project**: Developed as a real-world application of principles learned in **Harvard’s CS50x**.

---
*Developed by Jas Vohra*
