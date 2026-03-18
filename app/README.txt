This is a system that uses Docker containers to retrieve items from the Google RSS feed of a user-provided topic and
allows for an analysis of the recent news on said topic to be run. From this folder, run: docker compose up --build ,
and access localhost:8080 to see the UI. The project's structure is:
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

Browser provides the UI, web provides the reasoning behind the UI, Retrieval collects articles from the internet,
Analysis aggregates key pieces of information from these records, and DB provides a shared persistence.