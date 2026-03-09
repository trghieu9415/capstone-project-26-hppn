package io.hppn.unirag.service.impl;

import io.hppn.unirag.dto.tag.TagDTO;
import io.hppn.unirag.dto.tag.request.TagUpsertDTO;
import io.hppn.unirag.mapper.TagMapper;
import io.hppn.unirag.persistence.entity.TagEntity;
import io.hppn.unirag.persistence.repository.TagRepository;
import io.hppn.unirag.service.TagService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class TagServiceImpl implements TagService {

    private final TagRepository tagRepository;
    private final TagMapper tagMapper;

    @Override
    public TagDTO getById(UUID id) {
        return tagRepository.findById(id)
            .map(tagMapper::toDto)
            .orElseThrow(() -> new EntityNotFoundException("Tag not found"));
    }

    @Override
    public List<TagDTO> getAll() {
        return tagRepository.findAll().stream()
            .map(tagMapper::toDto)
            .collect(Collectors.toList());
    }

    @Override
    @Transactional
    public TagDTO upsert(TagUpsertDTO dto) {
        TagEntity entity;
        if (dto.id().isPresent()) {
            entity = tagRepository.findById(dto.id().get())
                .orElseThrow(() -> new EntityNotFoundException("Tag not found"));
            tagMapper.updateEntity(entity, dto);
        } else {
            // Có thể thêm logic check existsByName ở đây để ném lỗi nếu trùng tên
            entity = tagMapper.toEntity(dto);
        }
        return tagMapper.toDto(tagRepository.save(entity));
    }

    @Override
    @Transactional
    public void delete(UUID id) {
        tagRepository.deleteById(id);
    }
}