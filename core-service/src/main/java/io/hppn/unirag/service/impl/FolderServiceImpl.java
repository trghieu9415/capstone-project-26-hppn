package io.hppn.unirag.service.impl;

import io.hppn.unirag.dto.folder.FolderDTO;
import io.hppn.unirag.dto.folder.request.FolderUpsertDTO;
import io.hppn.unirag.mapper.FolderMapper;
import io.hppn.unirag.persistence.entity.FolderEntity;
import io.hppn.unirag.persistence.repository.FolderRepository;
import io.hppn.unirag.service.FolderService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
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
        // Lưu ý: Trong thực tế bro có thể cần check xem folder có document
        // hoặc folder con bên trong không trước khi xóa.
        folderRepository.deleteById(id);
    }
}