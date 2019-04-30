from typing import Dict, List, Union


class TaskRunner:
    def execute(self, parameter: str):
        raise NotImplemented(f'Execute method not implemented.')


class TrimTask(TaskRunner):
    def execute(self, parameter: str) -> Union[None,str]:
        if parameter is None:
            return None
        subject, trim = parameter.split(",", maxsplit=1)
        try:
            index_of_trim = subject.index(trim)
            return subject[:index_of_trim]
        except ValueError:
            return subject


__METHODS__ : Dict[str, TaskRunner] = {}


def __register_task__(task: TaskRunner, names=List[str]):
    for name in names:
        __METHODS__[name] = task


def __get_method__(name: str) -> TaskRunner:
    return __METHODS__[name]


def transform(method_name: str, input: str) -> str:
    task = __get_method__(method_name)
    return task.execute(input)


def is_variable_method(name : str):
    return name in __METHODS__


# Set up module data
__register_task__(TrimTask(), ['t', 'trim'])

