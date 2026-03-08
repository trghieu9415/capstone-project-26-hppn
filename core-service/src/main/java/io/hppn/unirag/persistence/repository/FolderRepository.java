package io.hppn.unirag.persistence.repository;

import io.hppn.unirag.persistence.entity.FolderEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface FolderRepository extends JpaRepository<FolderEntity, UUID> {
    List<FolderEntity> findByParentIdIsNull();

    List<FolderEntity> findByParentId(UUID parentId);

    List<FolderEntity> findByPathStartingWith(String pathPrefix);
}