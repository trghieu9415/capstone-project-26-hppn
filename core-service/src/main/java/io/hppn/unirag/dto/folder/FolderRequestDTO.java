package io.hppn.unirag.dto.folder;

import java.util.UUID;

public record FolderRequestDTO(
    String name,
    UUID parentId
) {
}