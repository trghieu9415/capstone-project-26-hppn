from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DocumentMetadata(_message.Message):
    __slots__ = ("document_id", "user_id", "file_name", "folder_id", "tags")
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    document_id: str
    user_id: str
    file_name: str
    folder_id: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, document_id: _Optional[str] = ..., user_id: _Optional[str] = ..., file_name: _Optional[str] = ..., folder_id: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class DocumentFilter(_message.Message):
    __slots__ = ("user_id", "document_id", "folder_id", "tags")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    document_id: str
    folder_id: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, user_id: _Optional[str] = ..., document_id: _Optional[str] = ..., folder_id: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class IngestRequest(_message.Message):
    __slots__ = ("file_content", "file_extension", "metadata")
    FILE_CONTENT_FIELD_NUMBER: _ClassVar[int]
    FILE_EXTENSION_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    file_content: bytes
    file_extension: str
    metadata: DocumentMetadata
    def __init__(self, file_content: _Optional[bytes] = ..., file_extension: _Optional[str] = ..., metadata: _Optional[_Union[DocumentMetadata, _Mapping]] = ...) -> None: ...

class IngestResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class QueryRequest(_message.Message):
    __slots__ = ("query", "top_k", "filter")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    TOP_K_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    query: str
    top_k: int
    filter: DocumentFilter
    def __init__(self, query: _Optional[str] = ..., top_k: _Optional[int] = ..., filter: _Optional[_Union[DocumentFilter, _Mapping]] = ...) -> None: ...

class QueryResponse(_message.Message):
    __slots__ = ("answer",)
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    answer: str
    def __init__(self, answer: _Optional[str] = ...) -> None: ...

class QueryStreamResponse(_message.Message):
    __slots__ = ("chunk",)
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    chunk: str
    def __init__(self, chunk: _Optional[str] = ...) -> None: ...
