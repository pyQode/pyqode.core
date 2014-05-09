from pyqode.core.backend import workers


def test_echo_worker():
    data = b'some data'
    status, ret_val = workers.echo_worker(data)
    assert status
    assert data == ret_val


def test_code_completion_worker():
    assert len(workers.CodeCompletionWorker.providers) == 0
    workers.CodeCompletionWorker.providers.append(
        workers.DocumentWordsProvider())
    assert len(workers.CodeCompletionWorker.providers) == 1
    worker = workers.CodeCompletionWorker()
    assert len(worker.providers) == 1
    with open(__file__, 'r') as f:
        code = f.read()
    data = {
        'code': code,
        'line': 1,
        'column': 0,
        'path': '',
        'encoding': 'utf-8',
        'prefix': ''
    }
    status, completion_groups = worker(data)
    assert status
    assert len(completion_groups)
    assert len(completion_groups[0])
    print(completion_groups)
    found = False
    for completions in completion_groups:
        for c in completions:
            if c['name'] == 'test_code_completion_worker':
                found = True
                break
    assert found
