package io.hppn.unirag.service;

import io.hppn.unirag.dto.tag.TagDTO;
import io.hppn.unirag.dto.tag.TagRequestDTO;

import java.util.List;

public interface TagService {
    TagDTO createTag(TagRequestDTO request);

    List<TagDTO> getAllTags();
}