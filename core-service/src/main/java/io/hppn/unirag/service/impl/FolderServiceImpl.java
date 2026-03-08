package io.hppn.unirag.service.impl;

import io.hppn.unirag.dto.folder.FolderDTO;
import io.hppn.unirag.dto.folder.FolderRequestDTO;
import io.hppn.unirag.dto.folder.FolderTreeDTO;
import io.hppn.unirag.mapper.FolderMapper;
import io.hppn.unirag.persistence.entity.FolderEntity;
import io.hppn.unirag.persistence.repository.FolderRepository;
import io.hppn.unirag.service.FolderService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class FolderServiceImpl implements FolderService {

    private final FolderRepository folderRepository;
    private final FolderMapper folderMapper;

    @Override
    @Transactional
    public FolderDTO createFolder(FolderRequestDTO request) {
        String path = "/";
        if (request.parentId() != null) {
            FolderEntity parent = folderRepository.findById(request.parentId())
                .orElseThrow(() -> new IllegalArgumentException("Parent folder not found"));
            path = parent.getPath() + parent.getId() + "/";
        }

        FolderEntity folder = FolderEntity.builder()
            .name(request.name())
            .parentId(request.parentId())
            .path(path)
            .build();

        return folderMapper.toDto(folderRepository.save(folder));
    }

    @Override
    @Transactional(readOnly = true)
    public List<FolderTreeDTO> getFolderTree() {
        List<FolderEntity> allFolders = folderRepository.findAll();

        Map<UUID, List<FolderEntity>> foldersByParent = allFolders.stream()
            .filter(f -> f.getParentId() != null)
            .collect(Collectors.groupingBy(FolderEntity::getParentId));

        return allFolders.stream()
            .filter(f -> f.getParentId() == null)
            .map(root -> buildTree(root, foldersByParent))
            .toList();
    }

    private FolderTreeDTO buildTree(FolderEntity folder, Map<UUID, List<FolderEntity>> foldersByParent) {
        List<FolderTreeDTO> children = foldersByParent.getOrDefault(folder.getId(), List.of())
            .stream()
            .map(child -> buildTree(child, foldersByParent))
            .toList();

        return new FolderTreeDTO(
            folder.getId(),
            folder.getName(),
            folder.getParentId(),
            children
        );
    }
}