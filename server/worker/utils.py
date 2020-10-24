from .tasks import dramatiq


def get_queue_items(queue_name='default'):
    import base64
    import json

    tasks = dramatiq.broker.client.lrange(f'dramatiq:{queue_name}', 0, -1)

    decoded_tasks = []
    for task in tasks:
        print(task)
        j = json.loads(task)
        body = json.loads(base64.b64decode(j['body']))
        decoded_tasks.append(body)

    return decoded_tasks
