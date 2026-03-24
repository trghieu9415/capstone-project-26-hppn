package io.hppn.unirag.dto.systemnode;

import java.util.List;
import java.util.UUID;

public record SystemNodeDTO(
    UUID id,
    String name,
    UUID parentId,
    SystemNodeType type,
    List<UUID> tagIds
) {
    public SystemNodeDTO(UUID id, String name, UUID parentId, SystemNodeType type) {
        this(id, name, parentId, type, List.of());
    }
}
