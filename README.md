# VGAC Microservices

Current tagging and database access tools for annotated images for VGAC

Link to Paper: [EXAG 2019](http://www.exag.org/papers/EXAG_2019_paper_13.pdf)

## Table of Contents

- [Installation](#installation)
- [File Breakdown](#file-breakdown)


## File breakdown

db_manager.py:

Ingests data into database from filesystem
Exports data to filesystem

10 Affordances per tag
RGB PNG images ingested in BLOB data columns
10-channel .npy affordance maps converted to black and white
