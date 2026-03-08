package io.hppn.unirag.provider;

import java.util.List;
import java.util.UUID;

public interface RagSyncProvider {
    boolean deleteDocumentVectors(UUID documentId);

    boolean updateDocumentMetadata(UUID documentId, UUID newFolderId, List<UUID> newTagIds);
}
