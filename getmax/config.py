
import errno
import json
import os
import typing as t


class Config(dict):
    def __init__(self, root_path: str, defaults: t.Optional[dict] = None) -> None:
        dict.__init__(self, defaults or {})
        self.root_path = root_path

    def from_object(self, obj: object) -> None:
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def from_file(
        self,
        filename: str,
        load: t.Callable[[t.IO[t.Any]], t.Mapping],
        silent: bool = False,
    ) -> bool:

        filename = os.path.join(self.root_path, filename)

        try:
            with open(filename) as f:
                obj = load(f)
        except OSError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False

            e.strerror = f"Unable to load configuration file ({e.strerror})"
            raise

        return self.from_mapping(obj)

    def from_mapping(
        self, mapping: t.Optional[t.Mapping[str, t.Any]] = None, **kwargs: t.Any
    ) -> bool:
        mappings: t.Dict[str, t.Any] = {}
        if mapping is not None:
            mappings.update(mapping)
        mappings.update(kwargs)
        for key, value in mappings.items():
            if key.isupper():
                self[key] = value
        return True

    def from_json(self, filename: str, silent: bool = False) -> bool:
        return self.from_file(filename, json.load, silent=silent)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {dict.__repr__(self)}>"
