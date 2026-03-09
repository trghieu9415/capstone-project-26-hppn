package io.hppn.unirag.dto.folder;

import java.time.LocalDateTime;
import java.util.UUID;

public record FolderDTO(
    UUID id,
    String name,
    UUID parentId,
    LocalDateTime createdAt
) {
}