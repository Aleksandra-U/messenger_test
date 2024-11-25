from app.tasks.celery import celery

# from celery import shared_task

import httpx

@celery.task #ИМЕННО ТАК 
def send_msg_task(chat_id, text): 
    token = '7586292019:AAHChEgA_fkbVNNXr71VumfWlob2RAMMkIk' 
    url_req = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}' 
    with httpx.Client() as client: 
        result = client.get(url_req)
    return result.status_code




# принимает словарик список строчку