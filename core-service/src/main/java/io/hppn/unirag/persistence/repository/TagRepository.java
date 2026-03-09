package io.hppn.unirag.persistence.repository;

import io.hppn.unirag.persistence.entity.TagEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface TagRepository extends JpaRepository<TagEntity, UUID> {

    Optional<TagEntity> findByName(String name);

    boolean existsByName(String name);
}