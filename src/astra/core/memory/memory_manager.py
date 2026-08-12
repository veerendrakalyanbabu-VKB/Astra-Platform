import json
from pathlib import Path


class MemoryManager:
    """
    Astra Memory Manager
    --------------------
    Responsible for storing and retrieving
    persistent information for Astra.
    """

    def __init__(self):

        self.data_folder = Path("data")
        self.data_folder.mkdir(exist_ok=True)

        self.memory_file = self.data_folder / "memory.json"

        if not self.memory_file.exists():

            with open(self.memory_file, "w", encoding="utf-8") as file:
                json.dump({}, file, indent=4)

        self.memory = self.load()

    def load(self):

        with open(self.memory_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def save(self):

        with open(self.memory_file, "w", encoding="utf-8") as file:
            json.dump(self.memory, file, indent=4)

    def remember(self, key, value):

        self.memory[key] = value

        self.save()

    def recall(self, key):

        return self.memory.get(key)

    def forget(self, key):

        if key in self.memory:

            del self.memory[key]

            self.save()

    def exists(self, key):

        return key in self.memory

    def list_all(self):

        return self.memory

    def search(self, query: str) -> dict:
        """
        Find memory entries matching a natural language query.
        Matches against keys and values.
        """

        if not query:
            return {}

        normalized_query = query.lower().strip()
        query_key = normalized_query.replace(" ", "_")
        results = {}

        if normalized_query in self.memory:
            results[normalized_query] = self.memory[normalized_query]

        if query_key in self.memory:
            results[query_key] = self.memory[query_key]

        for key, value in self.memory.items():
            key_lower = key.lower()
            value_lower = str(value).lower()

            if (
                normalized_query in key_lower
                or normalized_query in value_lower
                or query_key in key_lower
            ):
                results[key] = value

        return results

    def recall_best(self, query: str):
        """
        Return the best matching memory value for a query.
        """

        results = self.search(query)

        if not results:
            return None

        query_key = query.lower().strip().replace(" ", "_")

        if query_key in results:
            return results[query_key]

        return next(iter(results.values()))

    def reconfigure(self, data_folder: Path) -> None:
        self.data_folder = Path(data_folder)
        self.data_folder.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.data_folder / "memory.json"

        if not self.memory_file.exists():
            with open(self.memory_file, "w", encoding="utf-8") as file:
                json.dump({}, file, indent=4)

        self.memory = self.load()