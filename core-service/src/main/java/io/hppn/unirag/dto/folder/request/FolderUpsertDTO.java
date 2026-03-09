package io.hppn.unirag.dto.folder.request;

import java.util.Optional;
import java.util.UUID;

public record FolderUpsertDTO(
    Optional<UUID> id,
    String name,
    UUID parentId
) {
}