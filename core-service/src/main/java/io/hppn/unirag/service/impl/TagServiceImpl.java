package io.hppn.unirag.service.impl;

import io.hppn.unirag.dto.tag.TagDTO;
import io.hppn.unirag.dto.tag.TagRequestDTO;
import io.hppn.unirag.mapper.TagMapper;
import io.hppn.unirag.persistence.entity.TagEntity;
import io.hppn.unirag.persistence.repository.TagRepository;
import io.hppn.unirag.service.TagService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class TagServiceImpl implements TagService {

    private final TagRepository tagRepository;
    private final TagMapper tagMapper;

    @Override
    @Transactional
    public TagDTO createTag(TagRequestDTO request) {
        return tagRepository.findByName(request.name())
            .map(tagMapper::toDto)
            .orElseGet(() -> {
                TagEntity newTag = TagEntity.builder()
                    .name(request.name())
                    .colorCode(request.colorCode())
                    .build();
                return tagMapper.toDto(tagRepository.save(newTag));
            });
    }

    @Override
    @Transactional(readOnly = true)
    public List<TagDTO> getAllTags() {
        return tagRepository.findAll()
            .stream()
            .map(tagMapper::toDto)
            .toList();
    }
}