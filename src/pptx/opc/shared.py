"""Objects shared by modules in the pptx.opc sub-package."""

from __future__ import annotations

from typing import Any


class CaseInsensitiveDict(dict[str, Any]):
    """Mapping type like dict except it matches key without respect to case.

    For example, D['A'] == D['a']. Note this is not general-purpose, just complete
    enough to satisfy opc package needs. It assumes str keys for example.
    """

    def __contains__(self, key: object):
        if not isinstance(key, str):
            return False
        return super(CaseInsensitiveDict, self).__contains__(key.lower())

    def __getitem__(self, key: object):
        if not isinstance(key, str):
            raise KeyError(key)
        return super(CaseInsensitiveDict, self).__getitem__(key.lower())

    def __setitem__(self, key: str, value: Any):
        return super(CaseInsensitiveDict, self).__setitem__(key.lower(), value)
