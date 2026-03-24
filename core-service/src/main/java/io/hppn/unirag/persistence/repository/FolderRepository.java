package io.hppn.unirag.persistence.repository;

import io.hppn.unirag.dto.systemnode.DocumentTagMapping;
import io.hppn.unirag.dto.systemnode.SystemNodeDTO;
import io.hppn.unirag.persistence.entity.FolderEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface FolderRepository extends JpaRepository<FolderEntity, UUID> {
    List<FolderEntity> findByParentId(UUID parentId);

    List<FolderEntity> findByParentIsNull();

    @Query("""
            SELECT new io.hppn.unirag.dto.systemnode.SystemNodeDTO(
                f.id, f.name, f.parent.id, io.hppn.unirag.dto.systemnode.SystemNodeType.FOLDER
            ) FROM FolderEntity f
            UNION ALL
            SELECT new io.hppn.unirag.dto.systemnode.SystemNodeDTO(
                d.id, d.name, d.folder.id, io.hppn.unirag.dto.systemnode.SystemNodeType.DOCUMENT
            ) FROM DocumentEntity d
        """)
    List<SystemNodeDTO> findBaseSystemNodes();

    @Query("""
            SELECT new io.hppn.unirag.dto.systemnode.DocumentTagMapping(d.id, t.id)
            FROM DocumentEntity d
            JOIN d.tags t
            WHERE d.id IN :docIds
        """)
    List<DocumentTagMapping> findTagMappingsByDocumentIds(@Param("docIds") List<UUID> docIds);
}