package io.hppn.unirag.mapper;

import io.hppn.unirag.dto.tag.TagDTO;
import io.hppn.unirag.dto.tag.request.TagUpsertDTO;
import io.hppn.unirag.persistence.entity.TagEntity;
import org.mapstruct.*;

import java.util.Optional;
import java.util.UUID;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface TagMapper {

    TagDTO toDto(TagEntity entity);

    @Mapping(target = "id", expression = "java(unwrapOptional(dto.id()))")
    TagEntity toEntity(TagUpsertDTO dto);

    @Mapping(target = "id", ignore = true)
    void updateEntity(@MappingTarget TagEntity entity, TagUpsertDTO dto);

    default UUID unwrapOptional(Optional<UUID> optionalId) {
        return optionalId != null ? optionalId.orElse(null) : null;
    }
}