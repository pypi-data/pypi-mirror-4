from asynccall import AsyncResult

class LazyDict(dict):
    def __getitem__(self, key):
        _result = super(LazyDict, self).__getitem__(key)
        if isinstance(_result, AsyncResult):
            _result = _result._result
            self.__setitem__(key, _result)
        return _result