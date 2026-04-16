        Build a full-stack task management web application called "TaskFlow" with the following requirements:

        ## Backend (Python Flask REST API)
        - User authentication with JWT tokens (register, login, logout)
        - SQLAlchemy ORM with SQLite database
        - RESTful API endpoints for:
          - Projects: CRUD operations, assign team members
          - Tasks: CRUD with status (todo/in-progress/done), priority (low/medium/high/critical), due dates, assignee
          - Comments: add comments to tasks with timestamps
          - Dashboard: aggregate stats (tasks by status, overdue tasks, team workload)
        - Input validation and proper error handling with HTTP status codes
        - API rate limiting middleware
        - Logging with rotation

        ## Frontend (HTML/CSS/JavaScript - no framework)
        - Login/Register pages
        - Dashboard with charts showing project progress and task distribution
        - Kanban board view for tasks (drag-and-drop between columns)
        - Project list and detail views
        - Task creation/edit modal with form validation
        - Responsive design with CSS Grid/Flexbox

        ## DevOps & Quality
        - Dockerfile and docker-compose.yml for containerized deployment
        - Unit tests for all API endpoints using pytest
        - Database migration script
        - README.md with setup instructions, API documentation, and architecture overview
        - requirements.txt with all dependencies
        - .env.example for environment variables

        Save all files to taskflow/