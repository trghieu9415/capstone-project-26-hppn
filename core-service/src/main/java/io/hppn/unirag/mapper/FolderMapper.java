package io.hppn.unirag.mapper;

import io.hppn.unirag.dto.folder.FolderDTO;
import io.hppn.unirag.dto.folder.request.FolderUpsertDTO;
import io.hppn.unirag.persistence.entity.FolderEntity;
import org.mapstruct.*;

import java.util.Optional;
import java.util.UUID;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface FolderMapper {

    @Mapping(target = "parentId", source = "parent.id")
    FolderDTO toDto(FolderEntity entity);

    @Mapping(target = "id", expression = "java(unwrapOptional(dto.id()))")
    @Mapping(target = "parent", source = "parentId")
    @Mapping(target = "createdAt", ignore = true)
    FolderEntity toEntity(FolderUpsertDTO dto);

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "parent", source = "parentId")
    @Mapping(target = "createdAt", ignore = true)
    void updateEntity(@MappingTarget FolderEntity entity, FolderUpsertDTO dto);

    default UUID unwrapOptional(Optional<UUID> optionalId) {
        return optionalId != null ? optionalId.orElse(null) : null;
    }

    default FolderEntity mapParentById(UUID parentId) {
        if (parentId == null) return null;
        FolderEntity parent = new FolderEntity();
        parent.setId(parentId);
        return parent;
    }
}