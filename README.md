# webapp
 
Simple Flask application for user registration and management, including a basic health check endpoint.
## Getting Started


### Prerequisites
- Python 3.x
- MySQL database
  
### Installation
1. Clone the repository:

   ```bash
   git clone https://github.com/Saikiran8/webapp_remote.git

2. Create Virtual env

    ```bash
    cd webapp_remote
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt

3. Set up MySQL database:
    
    Create a MySQL database and update the environment variables in .env with your database credentials.

4. Run Application

    ```bash
    python app.py


## Endpoints
### Health Check:

1. URL: /healthz
    Method: GET
    Description: Returns health status of the application.
    User Registration:

2. URL: /v1/user
    Method: POST
    Description: Register a new user with the provided information.
    Get User Details:

3. URL: /v1/user/self
    Method: GET
    Description: Get details of the authenticated user.
    Update User Details:

4. URL: /v1/user/self
    Method: PUT
    Description: Update details of the authenticated user.
    
