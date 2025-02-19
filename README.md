# 🏋️ AI-Powered Fitness App


## 📌 What is this app?

This is your ultimate fitness companion, designed to help you start your workout journey effortlessly. The app tracks your training, sets realistic goals, and provides personalized recommendations to help you achieve your fitness objectives—whether it's weight loss, endurance improvement, or simply adopting a more active lifestyle.


## 🎯 Our Mission

Taking the first step is often the hardest part. That’s why we’ve designed an app specifically for beginners and those struggling with motivation.

According to the World Health Organization (WHO), obesity and cardiovascular diseases are becoming a major epidemic for future generations. Our mission is to promote a healthier lifestyle through technology, removing barriers for beginners and making fitness accessible to everyone.


## 🚀 How does it work?

### 💡 AI-Powered Personalized Training

    A machine learning model analyzes your progress and suggests the best exercises.
    The system evolves with you—the more you use it, the better the recommendations.

### 🎮 Motivation Made Easy

    Plans tailored to your fitness level and goals.

### 🛡 Safe & Adaptive Workouts

    Personalized recommendations based on your age, weight, fitness level, and health conditions.

## ⚠️ Disclaimer

This application provides AI-generated workout recommendations but does not replace professional advice from certified trainers, sports professionals, or healthcare providers. Before starting any workout plan, we strongly recommend consulting a doctor or a qualified fitness professional to ensure the activities are safe for you.


## ⚙️ Tech Stack

Below are the technologies used to implement this solution. It is recommended to install the specified versions to ensure compatibility:

### 🐍 [Python v3.12.8](https://www.python.org/downloads/release/python-3128/)

Chosen as the primary language due to its seamless integration with machine learning frameworks, extensive ecosystem, and ease of development.
Enables efficient data processing and AI model deployment for workout predictions.

### 🧠 [TensorFlow v2.18.0](https://pypi.org/project/tensorflow/2.18.0/)

A leading open-source framework for training and deploying deep learning models.
Offers extensive community support and optimized performance for AI-based fitness recommendations.

### 🌐 [Flask v3.1.0](https://pypi.org/project/Flask/3.1.0/)

A lightweight and efficient Python web framework used to develop the REST API.
Provides an intuitive and flexible way to serve AI predictions and manage user interactions.

### 💿 MongoDB v5.0.31 (Recommended Version: Latest Stable)

A NoSQL database that stores workout history and user data in a flexible JSON-like format.
Optimized for scalability and real-time interactions with the REST API.

## 📁 Project Structure

- `src/app.py`: Main application file containing the Flask application setup, routes, and business logic.
- `Dockerfile.app`: Defines the Docker image for the application service.
- `Dockerfile.db`: Defines the Docker image for the database service.
- `docker-compose.yml`: Orchestrates the application and database services.
- `.env`: Environment variablses. This file must be created based on example.

## 🚀 Setup Instructions 🌚
### Creating the Admin User

To have an admin user in your database, you have two options:

1. **Automatically via init-db.js:**  
Add the following block to your `init-db.js` file in project root so that the admin user is created automatically when the MongoDB container starts:

    ```javascript
    use dbname
    dbname.createUser({
        user: "user",
        pwd: "pass",
        roles: [
            { role: "readWrite", db: "dbname" },
            { role: "dbAdmin", db: "dbname" }
        ]
    });
    ```

Replace `"user"`, `"pass"` and `"dbname"` with your desired admin credentials. **⚠️Warning:** Must be same as .env file or docker enviroment variables

2. **Manually via docker exec:**

Alternatively, you can create the admin user manually after the containers are up:

a. Start the containers in detached mode:

    ```bash
    docker-compose up --build -d
    ```

b. Access the MongoDB container:

    ```bash
    docker exec -it <db_container_name> mongo -u user -p user --authenticationDatabase admin
    ```

Replace `<db_container_name>` with the name of your MongoDB container (use `docker ps` to list container names). Replace `"user"` and `"pass"` with your desired admin credentials. **⚠️Warning:** Must be same as .env file or docker enviroment variables

c. In the MongoDB shell, switch to your database and create the admin user:

    ```javascript
    use dbname
    dbname.createUser({
        user: "user",
        pwd: "pass",
        roles: [
            { role: "readWrite", db: "dbname" },
            { role: "dbAdmin", db: "dbname" }
        ]
    });
    ```

Replace `"user"`, `"pass"` and `"dbname"` with your desired admin credentials. **⚠️Warning:** Must be same as .env file or docker enviroment variables

To set up and start all services with a custom `.env` file from the root of the project, follow these steps:

1. Create a `.env` file in the root directory of the project based on the `.env.example` template. You can use the following parameters:

   ```
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=db
   DB_PORT=27017
   DB_NAME=your_db_name
   HTTP_PORT=8080
   SECRET_KEY=your_secret_key
   REFRESH_KEY=your_refresh_key
   ```

   Replace `your_db_user`, `your_db_password`, `your_db_name`, `your_secret_key`, and `your_refresh_key` with your desired values.

   **⚠️Warning:** It is not recommended to modify the `DB_HOST` if you are launching the services directly from Docker Compose. The `DB_HOST` should only be modified if you are running the services separately.

2. Open a terminal and navigate to the root directory of the project.

3. Run the following command to start the services using Docker Compose:

   ```
   docker-compose up --build
   ```

   This command builds the images for the application and database services and starts the containers.

4. Access the application at `http://localhost:8080/ping` in your web browser.

5. To stop the services, you can use `CTRL+C` in the terminal or run:

   ```
   docker-compose down
   ```

### Aternative Setup
To set up and start all services with custom environment variables, follow these steps:

1. Open a terminal and navigate to the root directory of the project.

2. Run the following command to start the services using Docker Compose with custom environment variables:

   ```bash
   DB_USER=your_db_user DB_PASSWORD=your_db_password DB_HOST=db DB_PORT=27017 DB_NAME=your_db_name HTTP_PORT=8080 SECRET_KEY=your_secret_key REFRESH_KEY=your_refresh_key docker-compose up --build
   ```

   **⚠️Warning:** It is not recommended to modify the `DB_HOST` if you are launching the services directly from Docker Compose. The `DB_HOST` should only be modified if you are running the services separately.

   Replace `your_db_user`, `your_db_password`, `your_db_name`, `your_secret_key`, and `your_refresh_key` with your desired values.

3. Access the application at `http://localhost:8080/ping` in your web browser.

4. To stop the services, you can use `CTRL+C` in the terminal or run:

   ```bash
   docker-compose down
   ```

5. **Complete Uninstallation:** To completely uninstall the services and remove all data, including user profiles and exercise logs, you need to delete the Docker volumes. This will erase all data stored in the database. Run the following command:

   ```bash
   docker-compose down -v
   ```

## 📬 Contact

If you have any questions, feedback, or want to contribute to the project, feel free to reach out:

- 📧 [E-mail](mailto:villa.carlosjesus@gmail.com)
- 🐦 [X](https://x.com/nithbuster)
- 💼 [LinkedIn](www.linkedin.com/in/carvilgar1)
- 📂 GitHub Issues: Open an issue

We'd love to hear from you! 🚀