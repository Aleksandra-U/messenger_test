
#!/bin/bash

celery --app=app.tasks.celery worker --loglevel=info
