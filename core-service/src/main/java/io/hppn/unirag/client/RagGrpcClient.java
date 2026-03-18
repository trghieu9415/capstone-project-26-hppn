package io.hppn.unirag.client;

import reactor.core.publisher.Flux;

import java.util.List;
import java.util.UUID;
import java.util.function.Consumer;

public interface RagGrpcClient {
    void uploadDocument(UUID docId, String fileName, String extension, byte[] fileBytes);

    void deleteDocument(UUID docId);

    String queryRag(String question, List<UUID> docIds);

    Flux<String> queryRagStream(String question, List<UUID> docIds);
}
