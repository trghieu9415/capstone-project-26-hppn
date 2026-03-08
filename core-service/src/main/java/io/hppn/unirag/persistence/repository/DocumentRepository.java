package io.hppn.unirag.persistence.repository;

import io.hppn.unirag.persistence.entity.DocumentEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface DocumentRepository extends
    JpaRepository<DocumentEntity, UUID>,
    JpaSpecificationExecutor<DocumentEntity> {
    
    Page<DocumentEntity> findByFolderId(UUID folderId, Pageable pageable);

    Page<DocumentEntity> findByTitleContainingIgnoreCase(String keyword, Pageable pageable);

    List<DocumentEntity> findByAiStatus(DocumentEntity.AiProcessingStatus aiStatus);

    Page<DocumentEntity> findByTags_Id(UUID tagId, Pageable pageable);
}