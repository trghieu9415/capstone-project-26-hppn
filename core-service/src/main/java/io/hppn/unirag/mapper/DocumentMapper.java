package io.hppn.unirag.mapper;

import io.hppn.unirag.dto.document.DocumentDTO;
import io.hppn.unirag.persistence.entity.DocumentEntity;
import io.hppn.unirag.persistence.entity.FolderEntity;
import io.hppn.unirag.persistence.entity.TagEntity;
import org.mapstruct.*;

import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface DocumentMapper {
    @Mapping(target = "folder", source = "folder.id")
    DocumentDTO toDto(DocumentEntity entity);

    default FolderEntity mapFolderById(UUID id) {
        if (id == null) return null;
        FolderEntity folder = new FolderEntity();
        folder.setId(id);
        return folder;
    }

    default Set<TagEntity> mapTagsById(Set<UUID> tagIds) {
        if (tagIds == null) return null;
        return tagIds.stream().map(id -> {
            TagEntity tag = new TagEntity();
            tag.setId(id);
            return tag;
        }).collect(Collectors.toSet());
    }
}