from typing import TypedDict, NotRequired


class Chunk(TypedDict):
    text: str
    file: str
    type: str
    chunk_index: NotRequired[int]
    page: NotRequired[int | None]
    subject: NotRequired[str]
    sender: NotRequired[str]
    date: NotRequired[str]