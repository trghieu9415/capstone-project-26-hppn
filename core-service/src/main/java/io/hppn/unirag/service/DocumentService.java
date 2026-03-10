package io.hppn.unirag.service;

import io.hppn.unirag.dto.document.DocumentDTO;
import io.hppn.unirag.dto.document.request.DocumentUpdateDTO;

import java.util.UUID;

public interface DocumentService {
    DocumentDTO getById(UUID id);

    DocumentDTO create(UUID folder, String fileName, String extension, byte[] fileBytes);

    DocumentDTO update(UUID id, DocumentUpdateDTO dto);

    void delete(UUID id);
}