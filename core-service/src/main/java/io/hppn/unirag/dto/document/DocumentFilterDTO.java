package io.hppn.unirag.dto.document;

import java.util.Set;
import java.util.UUID;

public record DocumentFilterDTO(
    String keyword,
    UUID folderId,
    Set<UUID> tagIds,
    String fileExtension
) {
}