package io.hppn.unirag.persistence.repository;

import io.hppn.unirag.persistence.entity.DocumentEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface DocumentRepository extends JpaRepository<DocumentEntity, UUID> {
    List<DocumentEntity> findByFolderId(UUID folderId);

    @Query("SELECT d FROM DocumentEntity d JOIN d.tags t WHERE t.id = :tagId")
    List<DocumentEntity> findByTagId(UUID tagId);

    @Query("SELECT d.id FROM DocumentEntity d " +
        "LEFT JOIN d.tags t " +
        "WHERE (:folderIds IS NULL OR d.folder.id IN :folderIds) " +
        "AND (:tagIds IS NULL OR t.id IN :tagIds)")
    List<UUID> findIdsByFoldersAndTags(
        @Param("folderIds") List<UUID> folderIds,
        @Param("tagIds") List<UUID> tagIds
    );
}