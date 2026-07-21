import json
import redis

from celery import shared_task

from .models import Comment

redis_client = redis.Redis(
    host="redis",
    port=6379,
    db=0,
    decode_responses=True,
)

@shared_task
def save_comments():
    comments = redis_client.lrange("comments_queue", 0, -1)

    if not comments:
        return

    redis_client.delete("comments_queue")

    objs = []

    for item in comments:
        data = json.loads(item)

        objs.append(
            Comment(
                author_id=data["author_id"],
                startup_id=data["startup_id"],
                parent_id=data["parent_id"],
                content=data["content"],
            )
        )

    Comment.objects.bulk_create(objs)