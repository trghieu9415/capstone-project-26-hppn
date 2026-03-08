package io.hppn.unirag.mapper;

import io.hppn.unirag.dto.folder.FolderDTO;
import io.hppn.unirag.dto.folder.FolderSummaryDTO;
import io.hppn.unirag.persistence.entity.FolderEntity;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface FolderMapper {
    FolderDTO toDto(FolderEntity entity);

    FolderSummaryDTO toSummaryDto(FolderEntity entity);
}