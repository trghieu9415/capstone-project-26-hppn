package io.hppn.unirag.dto.folder;

import java.util.List;
import java.util.UUID;

public record FolderTreeDTO(
    UUID id,
    String name,
    UUID parentId,
    List<FolderTreeDTO> children
) {
}
