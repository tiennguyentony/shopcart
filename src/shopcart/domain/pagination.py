from dataclasses import dataclass
from math import ceil

MAX_PAGE_SIZE = 100


@dataclass(frozen=True)
class PageRequest:
    """A page of results. Pages are numbered from 1."""

    page: int = 1
    size: int = 10

    @property
    def offset(self) -> int:
        return self.page * self.size

    @property
    def limit(self) -> int:
        return self.size

    def pages_for(self, total: int) -> int:
        return max(1, ceil(total / self.size))
