# #!/bin/bash

# alembic upgrade head

# # Правильный синтаксис для запуска gunicorn
# gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000

#!/bin/bash

#в предыдущей версии база данных не супела создаться (не успели создаться таблицы и тд)
# а мы уже хотим сразу делать минрации не дожидаясь пока она будуеет готова. в этим ошибка

echo "Waiting for database to be ready..."
sleep 10

echo "Running alembic upgrade..."
alembic upgrade head
if [ $? -ne 0 ]; then
  echo "Alembic migration failed"
  exit 1
fi

echo "Starting gunicorn..."
gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000