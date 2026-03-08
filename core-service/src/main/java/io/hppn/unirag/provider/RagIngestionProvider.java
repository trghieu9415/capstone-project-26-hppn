package io.hppn.unirag.provider;

import io.hppn.unirag.persistence.entity.DocumentEntity;

import java.util.List;

public interface RagIngestionProvider {
    boolean notifyAiToProcessSingle(DocumentEntity document);

    boolean notifyAiToProcessBulk(List<DocumentEntity> documents);
}
