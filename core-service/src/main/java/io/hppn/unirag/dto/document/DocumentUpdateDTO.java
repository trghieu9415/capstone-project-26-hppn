package io.hppn.unirag.dto.document;

import java.util.Set;
import java.util.UUID;

public record DocumentUpdateDTO(
    String title,
    UUID folderId,
    Set<UUID> tagIds
) {
}