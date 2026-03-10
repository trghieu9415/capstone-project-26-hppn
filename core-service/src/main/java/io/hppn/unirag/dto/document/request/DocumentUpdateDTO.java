package io.hppn.unirag.dto.document.request;

import java.util.Set;
import java.util.UUID;

public record DocumentUpdateDTO(
    UUID folder,
    Set<UUID> tags,
    String name,
    String extension
) {
}
