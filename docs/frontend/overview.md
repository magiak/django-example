# Frontend Overview

**Location:** `frontend/`

## Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 19.x | UI library |
| TypeScript | 5.7 | Type safety |
| Tailwind CSS | 3.4 | Utility-first styling |
| Vite | 6.x | Build tool and dev server |

## Project Structure

```
frontend/
├── index.html              # HTML entry point
├── package.json            # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
├── vite.config.ts          # Vite config (includes API proxy)
├── tailwind.config.ts      # Tailwind content paths
├── postcss.config.js       # PostCSS plugins (Tailwind, autoprefixer)
│
└── src/
    ├── main.tsx            # React root mount
    ├── App.tsx             # Main app component (ticket dashboard)
    ├── index.css           # Tailwind directives (@tailwind base/components/utilities)
    │
    ├── api/                # API client functions
    │   ├── client.ts       # (planned) Base fetch wrapper
    │   ├── tickets.ts      # (planned) Ticket API calls
    │   ├── triage.ts       # (planned) Triage API calls
    │   └── teams.ts        # (planned) Teams API calls
    │
    ├── components/         # Reusable UI components
    │   ├── TicketList.tsx   # (planned)
    │   ├── TicketForm.tsx   # (planned)
    │   └── StatusPill.tsx   # (planned)
    │
    ├── hooks/              # Custom React hooks
    │   └── useTickets.ts   # (planned)
    │
    ├── types/              # TypeScript type definitions
    │   └── ticket.ts       # (planned) Mirrors backend schemas
    │
    └── pages/              # Page-level components
        └── Dashboard.tsx   # (planned)
```

## API Integration

The Vite dev server proxies `/api` requests to the Django backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    "/api": "http://backend:8000",
  },
},
```

This means frontend code calls `/api/tickets/` and Vite forwards it to Django. No CORS issues in development.

### Current Implementation

The `App.tsx` component fetches tickets directly:

```typescript
useEffect(() => {
  fetch("/api/tickets/")
    .then((res) => res.json())
    .then(setTickets);
}, []);
```

### Planned: Typed API Client

Future iterations will generate typed API clients from the Django Ninja OpenAPI schema using tools like [orval](https://orval.dev/):

```bash
npx orval --input http://localhost:8000/api/openapi.json --output src/api
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server (port 5173) |
| `npm run build` | TypeScript check + production build |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint |

## Adding a New Page

1. Create a component in `src/pages/NewPage.tsx`
2. Add API functions in `src/api/` if needed
3. Add types in `src/types/` mirroring backend schemas
4. Add the route in `App.tsx` (once React Router is added)
