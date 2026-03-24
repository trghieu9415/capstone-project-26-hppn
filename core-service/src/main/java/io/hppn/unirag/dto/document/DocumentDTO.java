package io.hppn.unirag.dto.document;

import io.hppn.unirag.dto.tag.TagDTO;

import java.time.LocalDateTime;
import java.util.Set;
import java.util.UUID;

public record DocumentDTO(
    UUID id,
    UUID folder,
    Set<TagDTO> tags,
    String name,
    String extension,
    LocalDateTime createdAt
) {
}