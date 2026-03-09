package io.hppn.unirag.dto.folder.request;

import java.util.UUID;

public record FolderUpsertDTO(
    UUID id,
    String name,
    UUID parentId
) {
}