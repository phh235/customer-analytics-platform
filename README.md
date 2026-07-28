# Customer Segmentation and Purchase Value Prediction System

A customer analytics platform that segments customers based on purchasing
behavior and predicts their future purchase value using machine learning.

## Core Capabilities

- Customer profile and transaction data management
- Behavior-based customer segmentation
- Future purchase value prediction
- Segment and model performance analytics

---

## Tech Stack

[![React](https://img.shields.io/badge/React-%2320232a.svg?logo=react&logoColor=%2361DAFB)](#)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=fff)](#)
[![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=fff)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![uv](https://img.shields.io/badge/uv-261230.svg?logo=uv&logoColor=#de5fe9)](#)
[![shadcn/ui](https://img.shields.io/badge/shadcn%2Fui-000?logo=shadcnui&logoColor=fff)](#)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-%2338B2AC.svg?logo=tailwind-css&logoColor=white)](#)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-%23316192.svg?logo=postgresql&logoColor=white)](#)

---

## Project Structure

```text
customer-analytics-platform/
├── .agents/
├── backend/          # FastAPI
├── frontend/         # React + Vite
├── .editorconfig
├── .env.example
├── .gitignore
├── AGENTS.md
├── package.json
├── pnpm-lock.yaml
├── pnpm-workspace.yaml
└── README.md
```

---

## Development

Requires Node.js `>= 22` (recommended LTS), pnpm `>= 10`, Python `>= 3.12`, and uv.

```bash
# Clone repository
git clone https://github.com/phh235/customer-analytics-platform.git
cd customer-analytics-platform

# Install all dependencies
pnpm setup

# Start frontend & backend
pnpm dev
```

### Run individually

```bash
# Frontend
pnpm dev:frontend

# Backend
pnpm dev:backend
```

---

## License

This project is developed for academic and research purposes only.
