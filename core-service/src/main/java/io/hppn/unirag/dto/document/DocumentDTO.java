package io.hppn.unirag.dto.document;

import java.time.LocalDateTime;
import java.util.Set;
import java.util.UUID;

public record DocumentDTO(
    UUID id,
    DocumentFolder folder,
    Set<DocumentTag> tags,
    String name,
    String extension,
    LocalDateTime createdAt
) {
}