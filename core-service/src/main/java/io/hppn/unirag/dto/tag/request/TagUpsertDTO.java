package io.hppn.unirag.dto.tag.request;

import java.util.Optional;
import java.util.UUID;

public record TagUpsertDTO(
    Optional<UUID> id,
    String name,
    String color
) {
}