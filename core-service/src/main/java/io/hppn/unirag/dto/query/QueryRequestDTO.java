package io.hppn.unirag.dto.query;

import java.util.List;
import java.util.UUID;

public record QueryRequestDTO(
    String question,
    List<UUID> docIds,
    List<UUID> folderIds,
    List<UUID> tagIds
) {
}