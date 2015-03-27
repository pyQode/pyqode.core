import pytest
from pyqode.core.backend import workers


def test_echo_worker():
    data = b'some data'
    ret_val = workers.echo_worker(data)
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
        'prefix': '',
        'request_id': 47
    }
    completion_groups = worker(data)
    context = completion_groups[0]
    completion_groups = completion_groups[1:]
    line, column, req_id = context
    assert req_id == 47
    assert line == 1
    assert column == 0
    import logging
    logging.info('groups %r' % completion_groups)
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

with open('test/files/foo.py', 'r') as f:
    foo_py = f.read()

@pytest.mark.parametrize('data, nb_expected', [
    ({
        'string': foo_py,
        'sub': 'import',
        'regex': False,
        'whole_word': False,
        'case_sensitive': True}, 2),
    ({
        'string': 'import importable;\nimport',
        'sub': 'import',
        'regex': False,
        'whole_word': False,
        'case_sensitive': True}, 3),
    ({
        'string': 'import importable;\nimport\n',
        'sub': 'import',
        'regex': False,
        'whole_word': True,
        'case_sensitive': True}, 2),
    ({
        'string': 'import importable;\nimport',
        'sub': 'import',
        'regex': False,
        'whole_word': True,
        'case_sensitive': True}, 2),
    ({
        'string': 'import importable;\nimport',
        'sub': 'mport',
        'regex': False,
        'whole_word': True,
        'case_sensitive': True}, 0),
    ({
        'string': 'import importable;\nimport',
        'sub': 'Import',
        'regex': False,
        'whole_word': True,
        'case_sensitive': True}, 0),
    ({
        'string': 'import importable;\nimport',
        'sub': 'Import',
        'regex': False,
        'whole_word': True,
        'case_sensitive': False}, 2),
    ({
        'string': 'import importable;\nimport',
        'sub': 'Import',
        'regex': True,
        'whole_word': False,
        'case_sensitive': False}, 3),
    ({
        'string': 'super().__init__(foo, eggs)\nsuper(Foo,self).__init__()',
        'sub': 'super\(\).',
        'regex': True,
        'whole_word': False,
        'case_sensitive': False}, 1),
    ({
        'string': 'super().__init__(foo, eggs)\nsuper(Foo,self).__init__()',
        'sub': '',
        'regex': True,
        'whole_word': False,
        'case_sensitive': False}, 0)
])
def test_find_all(data, nb_expected):
    results = workers.findall(data)
    assert len(results) == nb_expected
