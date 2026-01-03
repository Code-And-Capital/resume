from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


class JSONDataSource:
    """
    Data source abstraction for loading JSON files from disk.

    This class is responsible for:
    - Validating file existence
    - Loading and parsing JSON content
    - Exposing the parsed data in a controlled way

    It does NOT:
    - Interpret the schema
    - Validate business rules
    - Perform transformations

    Those responsibilities belong to higher layers.
    """

    def __init__(self, file_path: str | Path) -> None:
        """
        Initialize a JSON data source.

        Parameters
        ----------
        file_path : str or pathlib.Path
            Path to the JSON file to be loaded.
        """
        self._path = Path(file_path)
        self._data = None

    @property
    def path(self) -> Path:
        """Return the resolved path to the JSON file."""
        return self._path

    @property
    def data(self) -> Dict[str, Any]:
        """
        Return the loaded JSON data.

        Raises
        ------
        RuntimeError
            If the data has not been loaded yet.
        """
        if self._data is None:
            raise RuntimeError(
                "JSON data has not been loaded yet. Call `.load()` first."
            )
        return self._data

    def load(self) -> Dict[str, Any]:
        """
        Load and parse the JSON file.

        Returns
        -------
        dict
            Parsed JSON content.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        json.JSONDecodeError
            If the file content is not valid JSON.
        """
        if not self._path.exists():
            raise FileNotFoundError(f"JSON file not found: {self._path}")

        with self._path.open("r", encoding="utf-8") as f:
            self._data = json.load(f)

        if not isinstance(self._data, dict):
            raise ValueError("Top-level JSON structure must be an object (dict).")
