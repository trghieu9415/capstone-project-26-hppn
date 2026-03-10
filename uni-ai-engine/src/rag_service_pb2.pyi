from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UploadRequest(_message.Message):
    __slots__ = ("doc_id", "chunk_data")
    DOC_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_DATA_FIELD_NUMBER: _ClassVar[int]
    doc_id: str
    chunk_data: bytes
    def __init__(self, doc_id: _Optional[str] = ..., chunk_data: _Optional[bytes] = ...) -> None: ...

class UploadResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class DeleteRequest(_message.Message):
    __slots__ = ("doc_id",)
    DOC_ID_FIELD_NUMBER: _ClassVar[int]
    doc_id: str
    def __init__(self, doc_id: _Optional[str] = ...) -> None: ...

class DeleteResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class QueryRequest(_message.Message):
    __slots__ = ("question", "doc_ids")
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    DOC_IDS_FIELD_NUMBER: _ClassVar[int]
    question: str
    doc_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, question: _Optional[str] = ..., doc_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class QueryResponse(_message.Message):
    __slots__ = ("answer_chunk",)
    ANSWER_CHUNK_FIELD_NUMBER: _ClassVar[int]
    answer_chunk: str
    def __init__(self, answer_chunk: _Optional[str] = ...) -> None: ...
