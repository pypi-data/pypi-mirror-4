from ua2.ajax import accept_ajax
from celery.result import AsyncResult
from celery.utils.encoding import safe_repr

from ua2.celery.auth import auth_decorator


@accept_ajax
@auth_decorator
def task_status(request, task_id):
    """
    Different from djcelery.views.task_status:
       - not provide information about traceback
       - provide authorization decorator
    """
    result = AsyncResult(task_id)
    task_result = result.result
    if result.status == 'FAILURE':
        task_result = safe_repr(result.result)
        
    return {'task_id': task_id,
            'status': result.status,
            'result': task_result}
