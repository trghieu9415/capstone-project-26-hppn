package io.hppn.unirag.provider;

import io.hppn.unirag.dto.rag.RagResponseDTO;

import java.util.List;
import java.util.UUID;

public interface RagQueryProvider {
    RagResponseDTO askQuestion(String userMessage, UUID folderFilterId, List<UUID> tagFilterIds);
}