package io.hppn.unirag.service.impl;

import io.hppn.unirag.client.RagGrpcClient;
import io.hppn.unirag.dto.document.DocumentDTO;
import io.hppn.unirag.dto.document.request.DocumentUpdateDTO;
import io.hppn.unirag.mapper.DocumentMapper;
import io.hppn.unirag.persistence.entity.DocumentEntity;
import io.hppn.unirag.persistence.repository.DocumentRepository;
import io.hppn.unirag.persistence.repository.FolderRepository;
import io.hppn.unirag.persistence.repository.TagRepository;
import io.hppn.unirag.service.DocumentService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashSet;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class DocumentServiceImpl implements DocumentService {

    private final DocumentRepository documentRepository;
    private final FolderRepository folderRepository;
    private final TagRepository tagRepository;
    private final DocumentMapper documentMapper;
    private final RagGrpcClient ragGrpcClient;

    @Override
    public DocumentDTO getById(UUID id) {
        return documentRepository.findById(id)
            .map(documentMapper::toDto)
            .orElseThrow(() -> new EntityNotFoundException("Document not found"));
    }

    @Override
    public List<DocumentDTO> getByFolderId(UUID id) {
        return documentRepository.findByFolderId(id)
            .stream()
            .map(documentMapper::toDto)
            .collect(Collectors.toList());
    }

    @Override
    @Transactional
    public DocumentDTO create(UUID folderId, String fileName, String extension, byte[] fileBytes) {
        if (folderId == null) {
            throw new IllegalArgumentException("Folder ID không được để trống!");
        }
        var entity = new DocumentEntity();

        var folder = folderRepository.getReferenceById(folderId);
        if (folder == null) {
            throw new EntityNotFoundException("Folder with Id not found");
        }
        entity.setName(fileName);
        entity.setExtension(extension);
        entity.setFolder(folder);

        entity = documentRepository.save(entity);

        if (fileBytes != null && fileBytes.length > 0) {
            try {
                ragGrpcClient.uploadDocument(
                    entity.getId(),
                    entity.getName(),
                    entity.getExtension(),
                    fileBytes
                );
                System.out.println("Calling Python gRPC to upload doc: " + entity.getId());
            } catch (Exception e) {
                throw new RuntimeException("Failed to upload document to AI Engine", e);
            }
        }

        return documentMapper.toDto(entity);
    }

    @Override
    @Transactional
    public DocumentDTO update(UUID id, DocumentUpdateDTO dto) {
        DocumentEntity entity = documentRepository.findById(id)
            .orElseThrow(() -> new EntityNotFoundException("Không tìm thấy tài liệu với ID: " + id));

        if (dto.name() != null && !dto.name().isBlank()) {
            entity.setName(dto.name());
        }
        if (dto.extension() != null && !dto.extension().isBlank()) {
            entity.setExtension(dto.extension());
        }

        if (dto.folder() != null) {
            var folder = folderRepository.findById(dto.folder())
                .orElseThrow(() -> new EntityNotFoundException("Không tìm thấy Folder mới với ID: " + dto.folder()));
            entity.setFolder(folder);
        }

        if (dto.tags() != null) {
            var newTags = new HashSet<>(tagRepository.findAllById(dto.tags()));
            entity.getTags().clear();
            entity.getTags().addAll(newTags);
        }

        entity = documentRepository.save(entity);
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