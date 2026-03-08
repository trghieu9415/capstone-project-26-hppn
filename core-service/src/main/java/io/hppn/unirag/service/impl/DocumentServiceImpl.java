package io.hppn.unirag.service.impl;

import io.hppn.unirag.dto.document.DocumentDTO;
import io.hppn.unirag.dto.document.DocumentFilterDTO;
import io.hppn.unirag.dto.document.DocumentUpdateDTO;
import io.hppn.unirag.mapper.DocumentMapper;
import io.hppn.unirag.persistence.entity.DocumentEntity;
import io.hppn.unirag.persistence.entity.FolderEntity;
import io.hppn.unirag.persistence.entity.TagEntity;
import io.hppn.unirag.persistence.repository.DocumentRepository;
import io.hppn.unirag.persistence.repository.FolderRepository;
import io.hppn.unirag.persistence.repository.TagRepository;
import io.hppn.unirag.service.DocumentService;
import jakarta.persistence.criteria.Join;
import jakarta.persistence.criteria.Predicate;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class DocumentServiceImpl implements DocumentService {

    private final DocumentRepository documentRepository;
    private final FolderRepository folderRepository;
    private final TagRepository tagRepository;
    private final DocumentMapper documentMapper;

    @Override
    @Transactional
    public DocumentDTO updateDocument(UUID documentId, DocumentUpdateDTO request) {
        DocumentEntity document = documentRepository.findById(documentId)
            .orElseThrow(() -> new IllegalArgumentException("Document not found"));

        if (request.title() != null && !request.title().isBlank()) {
            document.setTitle(request.title());
        }

        if (request.folderId() != null) {
            FolderEntity folder = folderRepository.findById(request.folderId())
                .orElseThrow(() -> new IllegalArgumentException("Folder not found"));
            document.setFolder(folder);
        }

        if (request.tagIds() != null) {
            List<TagEntity> tags = tagRepository.findAllById(request.tagIds());
            document.setTags(Set.copyOf(tags));
        }

        return documentMapper.toDto(documentRepository.save(document));
    }

    @Override
    @Transactional(readOnly = true)
    public Page<DocumentDTO> getDocuments(DocumentFilterDTO filter, Pageable pageable) {
        Specification<DocumentEntity> spec = buildSpecification(filter);
        return documentRepository.findAll(spec, pageable).map(documentMapper::toDto);
    }

    private Specification<DocumentEntity> buildSpecification(DocumentFilterDTO filter) {
        return (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();

            if (filter.keyword() != null && !filter.keyword().isBlank()) {
                predicates.add(cb.like(cb.lower(root.get("title")), "%" + filter.keyword().toLowerCase() + "%"));
            }

            if (filter.folderId() != null) {
                predicates.add(cb.equal(root.get("folder").get("id"), filter.folderId()));
            }

            if (filter.fileExtension() != null && !filter.fileExtension().isBlank()) {
                predicates.add(cb.equal(root.get("fileExtension"), filter.fileExtension()));
            }

            if (filter.tagIds() != null && !filter.tagIds().isEmpty()) {
                Join<DocumentEntity, TagEntity> tagsJoin = root.join("tags");
                predicates.add(tagsJoin.get("id").in(filter.tagIds()));
                query.distinct(true);
            }

            return cb.and(predicates.toArray(new Predicate[0]));
        };
    }
}