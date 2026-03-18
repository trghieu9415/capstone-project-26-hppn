package io.hppn.unirag.controller;

import io.hppn.unirag.dto.tag.TagDTO;
import io.hppn.unirag.dto.tag.request.TagUpsertDTO;
import io.hppn.unirag.service.TagService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/api/tags")
@RequiredArgsConstructor
public class TagController {

    private final TagService tagService;

    @GetMapping
    public ResponseEntity<List<TagDTO>> getAllTags() {
        return ResponseEntity.ok(tagService.getAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<TagDTO> getTagById(@PathVariable UUID id) {
        return ResponseEntity.ok(tagService.getById(id));
    }

    @PostMapping
    public ResponseEntity<TagDTO> createTag(@RequestBody TagUpsertDTO request) {
        TagUpsertDTO createDto = new TagUpsertDTO(
            Optional.empty(),
            request.name(),
            request.color()
        );
        TagDTO created = tagService.upsert(createDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<TagDTO> updateTag(
        @PathVariable UUID id,
        @RequestBody TagUpsertDTO request) {

        TagUpsertDTO updateDto = new TagUpsertDTO(
            Optional.of(id),
            request.name(),
            request.color()
        );
        return ResponseEntity.ok(tagService.upsert(updateDto));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTag(@PathVariable UUID id) {
        tagService.delete(id);
        return ResponseEntity.noContent().build();
    }
}