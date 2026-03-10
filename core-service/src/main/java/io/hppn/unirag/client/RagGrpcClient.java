package io.hppn.unirag.client;

import java.util.List;
import java.util.UUID;
import java.util.function.Consumer;

public interface RagGrpcClient {
    void uploadDocument(UUID docId, String fileName, String extension, byte[] fileBytes);

    void deleteDocument(UUID docId);

    String queryRagSync(String question, List<UUID> docIds);

    void queryRagStream(String question, List<UUID> docIds, Consumer<String> onNextChunk);
}