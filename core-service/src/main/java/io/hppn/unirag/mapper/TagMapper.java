package io.hppn.unirag.mapper;

import io.hppn.unirag.dto.tag.TagDTO;
import io.hppn.unirag.persistence.entity.TagEntity;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface TagMapper {
    TagDTO toDto(TagEntity entity);
}