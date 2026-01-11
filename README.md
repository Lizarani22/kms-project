# Knowledge_management_system

# AI Knowledge Management System

This project is an **AI-powered knowledge management system** built with **FastAPI**. It allows support teams to manage articles, handle user authentication, and provide automatic article recommendations based on user tickets.  

---

## Features

- **User Management**: Register and login with hashed passwords and JWT authentication.  
- **Article Management**: Load articles from CSV and manage in-memory.  
- **Ticket Analysis**: Recommend relevant articles automatically based on ticket content.  
- **Statistics**: Track total articles and recommendation counts.  
- **CORS Enabled**: Works with frontend apps from any origin.

---

## Tech Stack

- **Backend**: FastAPI  
- **Server**: Uvicorn  
- **Authentication**: JWT (JSON Web Token)  
- **Password Security**: bcrypt via Passlib  
- **Data Storage**: CSV for articles (in-memory database)  

---

## Installation

1. Clone the repository:

```bash
git clone <repo-url>
cd <project-folder>/backend
