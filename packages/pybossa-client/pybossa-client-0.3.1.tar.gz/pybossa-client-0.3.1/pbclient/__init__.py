# -*- coding: utf-8 -*-
"""
    Dead simple pybossa client
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    A simple PyBossa client

    :license: MIT
"""

_opts = dict()

import requests
import json


def set(key, val):
    global _opts
    _opts[key] = val


def _pybossa_req(method, domain, id=None, payload=None, params=None):
    """
    Sends a JSON request

    Returns True if everything went well, otherwise it returns the status code of the response
    """
    headers = {'content-type': 'application/json'}
    url = _opts['endpoint'] + '/api/' + domain
    if id is not None:
        url += '/' + str(id)
    if params is None:
        params = dict()
    if 'api_key' in _opts:
        params['api_key'] = _opts['api_key']
    if method == 'get':
        r = requests.get(url, params=params)
    elif method == 'post':
        r = requests.post(url, params=params, headers=headers, data=json.dumps(payload))
    elif method == 'put':
        r = requests.put(url, params=params, headers=headers, data=json.dumps(payload))
    elif method == 'delete':
        r = requests.delete(url, params=params, headers=headers, data=json.dumps(payload))
    # print r.status_code, r.status_code / 100
    if r.status_code / 100 == 2:
        if r.text:
            return json.loads(r.text)
        else:
            return True
    else:
        return r.status_code


# app
class DomainObject(object):

    def __init__(self, data):
        self.__dict__['data'] = data

    def __getattr__(self, name):
        data = self.__dict__['data']
        if name == 'data':
            return data
        if name in data:
            return data[name]
        raise AttributeError('unknown attribute: ' + name)

    def __setattr__(self, name, value):
        data = self.__dict__['data']
        if name == 'data':
            self.__dict__['data'] = value
            return True
        if name in data:
            data[name] = value
            return True
        raise AttributeError('unknown attribute: ' + name)


class App(DomainObject):
    def __repr__(self):
        return 'pybossa.App("' + self.short_name + '", ' + str(self.id) + ')'


class Task(DomainObject):
    def __repr__(self):
        return 'pybossa.Task(' + str(self.id) + ')'


class TaskRun(DomainObject):
    def __repr__(self):
        return 'pybossa.TaskRun(' + str(self.id) + ')'


# Apps

def get_apps(limit=100, offset=0):
    """Returns a list of registered apps

    :param limit: Number of returned items, default 100
    :type limit: integer
    :param offset: Offset for the query, default 0
    :type offset: integer

    :rtype: list
    :returns: A list of PyBossa Applications

    """
    return [App(app_data) for app_data in _pybossa_req('get', 'app',
        params=dict(limit=limit, offset=offset))]


def get_app(app_id):
    """Returns a PyBossa Application for the app_id

    :param app_id: PyBossa Application ID
    :type app_id: integer
    :rtype: PyBossa Application
    :returns: A PyBossa Application object
    
    """
    return App(_pybossa_req('get', 'app', app_id))


def find_app(**kwargs):
    """Returns a list with matching app arguments
    
    :param kwargs: PyBossa Application members
    :rtype: list
    :returns: A list of application that match the kwargs

    """
    return [App(app_data) for app_data in _pybossa_req('get', 'app', params=kwargs)]


def create_app(name, short_name, description):
    """Creates an application

    :param name: PyBossa Application Name
    :type name: string
    :param short_name: PyBossa Application short name or slug
    :type short_name: string
    :param description: PyBossa Application description
    :type decription: string
    :returns: True -- the response status code

    
    """
    app = dict(name=name, short_name=short_name, description=description)
    return _pybossa_req('post', 'app', payload=app)


def update_app(app):
    """Updates an application app instance

    :param app: PyBossa Application
    :type app: PyBossa Application
    :returns: True -- the response status code

    
    """
    return _pybossa_req('put', 'app', app.id, payload=app.data)


def delete_app(app_id):
    """Deletes an Application with id = app_id

    :param app_id: PyBossa Application ID
    :type app_id: integer
    :returns: True -- the response status code
    
    """
    return _pybossa_req('delete', 'app', app_id)


# Tasks

def get_tasks(app_id, limit=100, offset=0):
    """Returns a list of tasks for a given application ID

    :param app_id: PyBossa Application ID
    :type app_id: integer
    :param limit: Number of returned items, default 100
    :type limit: integer
    :param offset: Offset for the query, default 0
    :type offset: integer
    :returns: True -- the response status code
    
    """
    return [Task(task_data) for task_data in _pybossa_req('get', 'task',
        params=dict(app_id=app_id, limit=limit, offset=offset))]


def find_tasks(app_id, **kwargs):
    """Returns a list of matched tasks for a given application ID

    :param app_id: PyBossa Application ID
    :type app_id: integer
    :param kwargs: PyBossa Task members
    :type info: dict
    :rtype: list
    :returns: A list of tasks that match the kwargs

    """

    kwargs['app_id'] = app_id
    return [Task(task_data) for task_data in _pybossa_req('get', 'task', params=kwargs)]


def create_task(app_id, info, n_answers=30, priority_0=0, quorum=0):
    """Creates a task for a given application ID

    :param app_id: PyBossa Application ID
    :type app_id: integer
    :param info: PyBossa Application info JSON field
    :type info: dict
    :param n_answers: Number of answers or TaskRuns per task, default 30
    :type n_answers: integer
    :param priority_0: Value between 0 and 1 indicating priority of task within App (higher = more important), default 0.0
    :type priority_0: float
    :param quorum: Number of times this task should be done by different users, default 0
    :type quorum: integer
    :returns: True -- the response status code
    """
    task = dict(
        app_id=app_id,
        info=info,
        state=0,
        calibration=0,
        priority_0=priority_0,
        n_answers=n_answers,
        quorum=quorum
    )
    return _pybossa_req('post', 'task', payload=task)


def update_task(task):
    """Updates a task for a given task ID
    
    :param task: PyBossa task
    
    """
    return _pybossa_req('put', 'task', task.id, payload=task.data)


def delete_task(task):
    """Deletes a task for a given task ID

    :param task: PyBossa task 

    """
    #: :arg task: A task
    status = _pybossa_req('delete', 'task', task.id, payload=dict(app_id=task.app_id))
    if status >= 300:
        status = 'status: %d' % status
        print 'could not delete task', task.id, '(%s)' % status


# Task Runs

def get_taskruns(app_id, limit=100, offset=0):
    """Returns a list of task runs for a given application ID

    :param app_id: PyBossa Application ID
    :type app_id: integer
    :param limit: Number of returned items, default 100
    :type limit: integer
    :param offset: Offset for the query, default 0
    :type offset: integer
    :rtype: list
    :returns: A list of task runs for the given application ID

    """
    return [TaskRun(task_data) for task_data in _pybossa_req('get', 'taskrun',
        params=dict(app_id=app_id, limit=limit, offset=offset))]


def find_taskruns(app_id, **kwargs):
    """Returns a list of matched task runs for a given application ID

    :param app_id: PyBossa Application ID
    :type app_id: integer
    :param kwargs: PyBossa Task Run members
    :rtype: list
    :returns: A List of task runs that match the query members

    """
    kwargs['app_id'] = app_id
    return [TaskRun(task_data) for task_data in _pybossa_req('get', 'taskrun', params=kwargs)]
