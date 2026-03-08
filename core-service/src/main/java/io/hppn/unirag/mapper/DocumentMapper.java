package io.hppn.unirag.mapper;

import io.hppn.unirag.dto.document.DocumentDTO;
import io.hppn.unirag.persistence.entity.DocumentEntity;
import org.mapstruct.Mapper;

@Mapper(
    componentModel = "spring",
    uses = {TagMapper.class, FolderMapper.class}
)
public interface DocumentMapper {
    DocumentDTO toDto(DocumentEntity entity);
}