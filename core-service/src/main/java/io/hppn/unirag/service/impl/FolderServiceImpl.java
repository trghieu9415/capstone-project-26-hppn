package io.hppn.unirag.service.impl;

import io.hppn.unirag.dto.folder.FolderDTO;
import io.hppn.unirag.dto.folder.request.FolderUpsertDTO;
import io.hppn.unirag.dto.systemnode.DocumentTagMapping;
import io.hppn.unirag.dto.systemnode.SystemNodeDTO;
import io.hppn.unirag.dto.systemnode.SystemNodeType;
import io.hppn.unirag.mapper.FolderMapper;
import io.hppn.unirag.persistence.entity.FolderEntity;
import io.hppn.unirag.persistence.repository.FolderRepository;
import io.hppn.unirag.service.FolderService;
import jakarta.persistence.EntityNotFoundException;
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
    public FolderDTO getById(UUID id) {
        return folderRepository.findById(id)
            .map(folderMapper::toDto)
            .orElseThrow(() -> new EntityNotFoundException("Folder not found"));
    }

    @Override
    public List<FolderDTO> getAll() {
        return folderRepository.findAll().stream()
            .map(folderMapper::toDto)
            .collect(Collectors.toList());
    }

    @Override
    @Transactional
    public FolderDTO upsert(FolderUpsertDTO dto) {
        FolderEntity entity;
        if (dto.id().isPresent()) {
            entity = folderRepository.findById(dto.id().get())
                .orElseThrow(() -> new EntityNotFoundException("Folder not found"));
            folderMapper.updateEntity(entity, dto);
        } else {
            entity = folderMapper.toEntity(dto);
        }
        return folderMapper.toDto(folderRepository.save(entity));
    }

    @Override
    @Transactional
    public void delete(UUID id) {
        folderRepository.deleteById(id);
    }

    @Override
    public List<SystemNodeDTO> getSystemNodes() {
        List<SystemNodeDTO> nodes = folderRepository.findBaseSystemNodes();

        List<UUID> documentIds = nodes.stream()
            .filter(node -> node.type() == SystemNodeType.DOCUMENT)
            .map(SystemNodeDTO::id)
            .toList();

        if (documentIds.isEmpty()) {
            return nodes;
        }

        List<DocumentTagMapping> tagMappings = folderRepository.findTagMappingsByDocumentIds(documentIds);

        Map<UUID, List<UUID>> tagsMap = tagMappings.stream()
            .collect(Collectors.groupingBy(
                DocumentTagMapping::documentId,
                Collectors.mapping(DocumentTagMapping::tagId, Collectors.toList())
            ));

        return nodes.stream().map(node -> {
            if (node.type() == SystemNodeType.DOCUMENT && tagsMap.containsKey(node.id())) {
                return new SystemNodeDTO(
                    node.id(),
                    node.name(),
                    node.parentId(),
                    node.type(),
                    tagsMap.get(node.id())
                );
            }
            return node;
        }).toList();
    }

}