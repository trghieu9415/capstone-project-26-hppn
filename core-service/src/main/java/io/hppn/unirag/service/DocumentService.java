package io.hppn.unirag.service;

import io.hppn.unirag.dto.document.DocumentDTO;
import io.hppn.unirag.dto.document.DocumentFilterDTO;
import io.hppn.unirag.dto.document.DocumentUpdateDTO;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.UUID;

public interface DocumentService {
    DocumentDTO updateDocument(UUID documentId, DocumentUpdateDTO request);

    Page<DocumentDTO> getDocuments(DocumentFilterDTO filter, Pageable pageable);
}