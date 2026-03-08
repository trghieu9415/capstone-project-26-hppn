package io.hppn.unirag.service;

import io.hppn.unirag.dto.folder.FolderDTO;
import io.hppn.unirag.dto.folder.FolderRequestDTO;
import io.hppn.unirag.dto.folder.FolderTreeDTO;

import java.util.List;

public interface FolderService {
    FolderDTO createFolder(FolderRequestDTO request);

    List<FolderTreeDTO> getFolderTree();
}