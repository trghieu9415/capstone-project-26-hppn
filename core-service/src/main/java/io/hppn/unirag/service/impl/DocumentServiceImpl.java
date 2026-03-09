package io.hppn.unirag.service.impl;

import io.hppn.unirag.client.RagGrpcClient;
import io.hppn.unirag.dto.document.DocumentDTO;
import io.hppn.unirag.dto.document.request.DocumentUpsertDTO;
import io.hppn.unirag.mapper.DocumentMapper;
import io.hppn.unirag.persistence.entity.DocumentEntity;
import io.hppn.unirag.persistence.repository.DocumentRepository;
import io.hppn.unirag.service.DocumentService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class DocumentServiceImpl implements DocumentService {

    private final DocumentRepository documentRepository;
    private final DocumentMapper documentMapper;
    private final RagGrpcClient ragGrpcClient;

    @Override
    public DocumentDTO getById(UUID id) {
        return documentRepository.findById(id)
            .map(documentMapper::toDto)
            .orElseThrow(() -> new EntityNotFoundException("Document not found"));
    }

    @Override
    @Transactional
    public DocumentDTO upsert(DocumentUpsertDTO dto, byte[] fileBytes) {
        DocumentEntity entity;
        boolean isCreate = dto.id().isEmpty();

        if (!isCreate) {
            entity = documentRepository.findById(dto.id().get())
                .orElseThrow(() -> new EntityNotFoundException("Document not found"));
            documentMapper.updateEntity(entity, dto);
            entity = documentRepository.save(entity);
        } else {
            entity = documentMapper.toEntity(dto);
            entity = documentRepository.save(entity);

            if (fileBytes != null && fileBytes.length > 0) {
                try {
                    ragGrpcClient.uploadDocument(entity.getId(), fileBytes);
                    System.out.println("Calling Python gRPC to upload doc: " + entity.getId());
                } catch (Exception e) {
                    throw new RuntimeException("Failed to upload document to AI Engine", e);
                }
            }
        }

        return documentMapper.toDto(entity);
    }

    @Override
    @Transactional
    public void delete(UUID id) {
        if (!documentRepository.existsById(id)) {
            throw new EntityNotFoundException("Document not found");
        }

        try {
            ragGrpcClient.deleteDocument(id);
            System.out.println("Calling Python gRPC to delete doc: " + id);
        } catch (Exception e) {
            throw new RuntimeException("Failed to delete document from AI Engine", e);
        }

        documentRepository.deleteById(id);
    }
}