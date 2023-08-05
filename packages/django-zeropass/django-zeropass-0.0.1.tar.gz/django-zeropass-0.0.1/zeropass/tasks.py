from celery import task

@task
def delete_token(token):
    try:
        token.delete()
    except AssertionError:
        pass
