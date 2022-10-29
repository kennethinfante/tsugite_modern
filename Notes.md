### Learnings

* When renaming variables, function parameters start with the least dependency (bottom of the graph)
* For `__init__.py`, `None` return type is Ok. But for methods that use other libraries, especially GUI libraries,
    they have implicity returns. Do not change the return type to `None`
* For `Buffer`, do not return None as well