This is a system that uses Docker containers to retrieve items from the Google RSS feed of a user-provided topic, stores it in a PostgreSQL database, and
analyzes trends via agent pipeline. Run docker compose up --build from the news-agent/app folder to start the project.
Access localhost:8080 to see the UI. The project's structure is:

[ Browser ]
     |
     v
   [ Web ]
   /     \
  v       v
[Retrieval]   [Analysis]
      \       /
        v   v
         [ DB ]

##CONTAINERS
-Browser: Provides the UI 
-Web: Provides the reasoning behind the UI
-Retrieval: Collects articles from the internet,
-Analysis: Aggregates key pieces of information from these records
-DB: Provides a shared persistent memory.

##STACK
- FastAPI (backend)
- React + Vite (frontend)
- PostgreSQL (database)
- Docker Compose