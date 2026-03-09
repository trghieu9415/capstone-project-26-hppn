package io.hppn.unirag.dto.document.request;

import java.util.Optional;
import java.util.Set;
import java.util.UUID;

public record DocumentUpsertDTO(
    Optional<UUID> id,
    UUID folder,
    Set<UUID> tags,
    String name,
    String extension
) {
}
