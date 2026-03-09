package io.hppn.unirag.service;

import io.hppn.unirag.dto.document.DocumentDTO;
import io.hppn.unirag.dto.document.request.DocumentUpsertDTO;

import java.util.UUID;

public interface DocumentService {
    DocumentDTO getById(UUID id);

    DocumentDTO upsert(DocumentUpsertDTO dto, byte[] fileBytes);

    void delete(UUID id);
}