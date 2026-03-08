package io.hppn.unirag.dto.tag;

import java.util.UUID;

public record TagDTO(
    UUID id,
    String name,
    String colorCode
) {
}