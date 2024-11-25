Project Launch Instructions:

To run the application with Docker: From the root folder, enter docker compose up -d.

...

Connect with the Telegram bot to receive notifications (works without Docker; likely issues with specifying the address and port in Docker):

1. Start the server: open Command Prompt. Enter the following command in the terminal: uvicorn app.main:app --reload.

2. The Celery worker only functions if the Redis server is running (not via Docker).

To run Redis: download Redis-7.4.0-Windows-x64-msys2-with-Service. Launch the redis-server file. Then, start the redis-cli file.

3. Start Celery: open a new window in Command Prompt.
Enter the following command in the terminal: celery -A app.tasks.celery worker --loglevel=INFO --pool=solo.

4. Search for the Telegram bot @my_Jessi_test_weather_bot.

5. Enter the command /start.

6. Input your username under which you registered in the application (this will be added to the database for sending notifications of new messages).

7. Done! The bot will send notifications about new messages if you are offline.

Project Functionality Description:

A real-time instant messaging service between users has been developed using WebSockets technology on the FastAPI framework.

The application allows for the registration of new users. After registration, the user must authenticate to access the site and its full functionality.

The main page displays users with whom there are existing dialogs. All conversations (and users) are saved in a PostgreSQL database (using Alembic for migrations and SQLAlchemy for database queries). When opening a chat window, conversations are loaded from the cache (Redis) if available. The main page includes a button to display all registered users, allowing messages to be sent (and received) from them.

A Telegram bot created with Aiogram notifies users of new messages (in the background via Celery) if the user is offline. IMPORTANT! To send notifications about new messages, a check is performed to see if the user is online or offline. A registered user in the database has a default field named "token" with a value of 0 (indicating offline status). When the user logs into the site, this value changes to 1 (indicating online status). The value will only change back to 0 (offline) upon clicking the "Logout" button. In this case, the token will be set to 0, and the bot will begin sending notifications about new messages. The JWT token will expire in the browser after 24 hours, but the token value in the database will not change automatically (only upon logout).

The code for handling requests is fully asynchronous. I did not see the need or opportunity to implement multithreading for improving performance.
