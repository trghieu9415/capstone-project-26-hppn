package io.hppn.unirag.service;

import io.hppn.unirag.dto.tag.TagDTO;
import io.hppn.unirag.dto.tag.request.TagUpsertDTO;

import java.util.List;
import java.util.UUID;

public interface TagService {
    TagDTO getById(UUID id);

    List<TagDTO> getAll();

    TagDTO upsert(TagUpsertDTO dto);

    void delete(UUID id);
}