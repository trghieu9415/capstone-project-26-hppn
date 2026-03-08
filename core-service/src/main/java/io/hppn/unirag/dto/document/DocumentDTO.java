package io.hppn.unirag.dto.document;

import io.hppn.unirag.dto.folder.FolderSummaryDTO;
import io.hppn.unirag.dto.tag.TagDTO;

import java.time.LocalDateTime;
import java.util.Set;
import java.util.UUID;

public record DocumentDTO(
    UUID id,
    String title,
    String originalFileName,
    Long fileSize,
    String fileExtension,
    FolderSummaryDTO folder,
    Set<TagDTO> tags,
    String aiStatus,
    LocalDateTime createdAt
) {
}