package io.hppn.unirag.mapper;

import io.hppn.unirag.dto.document.DocumentDTO;
import io.hppn.unirag.dto.document.DocumentFolder;
import io.hppn.unirag.dto.document.DocumentTag;
import io.hppn.unirag.dto.document.request.DocumentUpsertDTO;
import io.hppn.unirag.persistence.entity.DocumentEntity;
import io.hppn.unirag.persistence.entity.FolderEntity;
import io.hppn.unirag.persistence.entity.TagEntity;
import org.mapstruct.*;

import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface DocumentMapper {
    DocumentDTO toDto(DocumentEntity entity);

    DocumentFolder toDocumentFolderDto(FolderEntity folder);

    DocumentTag toDocumentTagDto(TagEntity tag);

    default Optional<DocumentFolder> mapParentFolder(FolderEntity parent) {
        return Optional.ofNullable(parent).map(this::toDocumentFolderDto);
    }

    @Mapping(target = "id", expression = "java(unwrapOptional(dto.id()))")
    @Mapping(target = "folder", source = "folder")
    @Mapping(target = "tags", source = "tags")
    @Mapping(target = "createdAt", ignore = true)
    DocumentEntity toEntity(DocumentUpsertDTO dto);

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    @Mapping(target = "folder", source = "folder")
    @Mapping(target = "tags", source = "tags")
    void updateEntity(@MappingTarget DocumentEntity entity, DocumentUpsertDTO dto);

    default UUID unwrapOptional(Optional<UUID> optionalId) {
        return optionalId != null ? optionalId.orElse(null) : null;
    }

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