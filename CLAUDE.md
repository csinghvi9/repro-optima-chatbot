# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IVF Chatbot — a healthcare chatbot application with a **Next.js frontend** and a **FastAPI (Python) backend**. The frontend serves as a real-time conversational UI with multi-language support, appointment booking, and an admin dashboard. It can also be deployed as an embeddable widget.

## Repository Structure

```
frontend/   — Next.js 15 (React 19, TypeScript, Tailwind CSS 4)
backend/    — FastAPI (Python 3.11+, MongoDB via Beanie, LangChain, OpenAI)
```

## Frontend Commands

All commands run from `frontend/`:

```bash
npm install              # Install dependencies
npm run dev              # Dev server with Turbopack on port 443
npm run build            # Production build
npm run start            # Production server on port 443
npm run lint             # ESLint
npx webpack --config webpack.widget.config.mjs  # Build embeddable widget bundle
```

## Backend

The backend uses **uv** (or poetry) for dependency management. See `backend/pyproject.toml`. Backend runs FastAPI with uvicorn and uses MongoDB (Beanie ODM), Redis, ChromaDB, and OpenAI/LangChain.

## Frontend Architecture

### Path Alias
`@/*` maps to `./src/*` (configured in tsconfig.json).

### Key Directories
- `src/app/` — Next.js App Router pages and layout. Two routes: `/` (chatbot) and `/admin` (dashboard).
- `src/components/container/` — Feature containers (bot_ui, admin_panel, login, bookFreeConsultation, ivfSuccessCalculator, findHospital, emiFacilities, ivfPackage, servicesOffered, frequentlyAskedQuestion, etc.)
- `src/components/ui/` — Reusable presentational components (calendar, timeSlots, centersList, feedbackBox, faqResponse, languageSelection, etc.)
- `src/components/constants/` — Centralized constants: `translations.ts` (11 languages), `labelMap.ts` (option-to-component mapping), `options.ts` (menu options), `botMessage.ts` (greeting messages)
- `src/components/messages/` — `message.hook.js` (useMessages custom hook)
- `src/components/threads/` — `threads.hook.js` (useThreads custom hook)
- `src/components/admin_auth/` — `auth.ts` (admin login & token refresh logic)
- `widget/` — Entry point for the embeddable UMD chatbot widget bundle

### State Management
- **WebSocketContext** (`src/app/WebSocketContext.tsx`) — React Context providing WebSocket connection, reconnection (max 5 retries with backoff), and message sending.
- **Custom hooks** — `useThreads()` for thread CRUD, `useMessages()` for message fetching via axios.
- **No global state library** — state is component-local with prop drilling. Context is used only for WebSocket.
- **sessionStorage** — stores `guest_token`, `admin_access_token`, `admin_refresh_token`.

### API Integration
- REST via **axios** against `NEXT_PUBLIC_API_BASE_URL`
- WebSocket via `NEXT_PUBLIC_WEBSOCKET_URL` at `/api/assistant/ws?token={token}`
- Key endpoints: `/api/auth/guest_token`, `/api/thread/*`, `/api/message/*`, `/api/admin_auth/login`

### Authentication
- **Guest**: auto-fetches JWT from `/api/auth/guest_token`, stored in sessionStorage
- **Admin**: email/password login, access + refresh tokens in sessionStorage, token refresh via `/auth/get_access_token_from_refresh_token`

### Internationalization
11 languages supported (English, Hindi, Marathi, Gujarati, Kannada, Tamil, Telugu, Bengali, Punjabi, Assamese, Odia). Translations in `src/components/constants/translations.ts`. Language selection happens at chatbot startup and persists via API call.

### Widget System
`webpack.widget.config.mjs` builds `widget/index.js` into `public/widget/chatbot.bundle.js` (UMD, global `ChatbotWidget`). CORS headers configured in `next.config.ts` for cross-origin embedding.

### Notable Integrations
- **Microsoft Azure Speech SDK** — voice input/output
- **@xenova/transformers** — client-side ML inference
- **Swiper** — carousel/slider for video messages
- **HeroUI Calendar** — date selection for appointments

## Conventions

- Mixed TypeScript and JavaScript (migrating toward TS). Strict mode enabled.
- Tailwind CSS for styling with custom design tokens (indira_red, indira_pink, indira_yellow, indira_blue) defined in `tailwind.config.js`.
- styled-components used selectively alongside Tailwind.
- `"use client"` directive required on interactive components (Next.js App Router).
- Dynamic component rendering via `componentMap` pattern in `labelMap.ts`.

## Local Docker Setup

From the repository root:

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8001

The root `docker-compose.yml` builds both services. The frontend is built with API URLs pointing to `localhost:8001`. The backend uses its existing `.env` (connects to remote Azure Cosmos DB, OpenAI, etc.).

To rebuild a single service: `docker compose up --build frontend` or `docker compose up --build backend`.

## Production Deployment

- **Docker**: multi-stage Dockerfile in both `frontend/` and `backend/` (exposes port 443 internally)
- **CI/CD**: Azure Pipelines (`azure-pipelines.yml`) → builds Docker image → pushes to AWS ECR → deploys to EC2
- **Build scripts**: `build_and_push.sh`, `build_and_push_azure_prod.sh`, `build_and_push_azure_uat.sh`

## Environment Variables

Required in `.env` (not committed):
- `NEXT_PUBLIC_API_BASE_URL` — Backend REST API URL
- `NEXT_PUBLIC_WEBSOCKET_URL` — Backend WebSocket URL
