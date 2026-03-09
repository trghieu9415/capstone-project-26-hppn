package io.hppn.unirag.dto.tag.request;

import java.util.UUID;

public record TagUpsertDTO(
    UUID id,
    String name,
    String colorCode
) {
}