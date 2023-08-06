# -*- coding: utf-8 *-*
"""Lets doit_ read tasks defined using classes, decorated functions or function
calls."""

class TaskBase(object):
    """Subclass this to define tasks."""
    @classmethod
    def create_doit_tasks(cls):
        if cls is TaskBase:
            return  # avoid create tasks from base class 'Task'
        instance = cls()
        kw = dict((a, getattr(instance, a)) \
                    for a in dir(instance) if not a.startswith('_'))

        kw.pop('create_doit_tasks')
        if 'actions' not in kw:
            kw['actions'] = [kw.pop('run')]
        if 'doc' not in kw and (cls.__doc__ != TaskBase.__doc__):
            kw['doc'] = cls.__doc__
        return kw


class task(object):
    """Use as a decorator, or call with arguments to make a task."""
    def __init__(self, _func=None, **meta):
        self.func = _func  # When used as a decorator without kwargs
        self.meta = meta   # When called with kwargs
        self.create_doit_tasks = self._create_doit_tasks

    def __call__(self, func):
        self.func = func  # When instantiated with kwargs & used as a decorator
        return self

    # Renamed at instantiation so that doit doesn't try to call the unbound
    # method.
    def _create_doit_tasks(self):
        task_dict = self.meta.copy()
        if self.func:
            task_dict.update(basename=self.func.__name__,
                             actions=[self.func]
                            )
        return task_dict
