package io.hppn.unirag.service;

import io.hppn.unirag.dto.folder.FolderDTO;
import io.hppn.unirag.dto.folder.request.FolderUpsertDTO;

import java.util.List;
import java.util.UUID;

public interface FolderService {
    FolderDTO getById(UUID id);

    List<FolderDTO> getAll();

    FolderDTO upsert(FolderUpsertDTO dto);

    void delete(UUID id);
}