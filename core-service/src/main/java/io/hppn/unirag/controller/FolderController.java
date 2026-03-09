package io.hppn.unirag.controller;

import io.hppn.unirag.dto.folder.FolderDTO;
import io.hppn.unirag.dto.folder.request.FolderUpsertDTO;
import io.hppn.unirag.service.FolderService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/api/folders")
@RequiredArgsConstructor
public class FolderController {

    private final FolderService folderService;

    // Lấy toàn bộ danh sách Folder
    @GetMapping
    public ResponseEntity<List<FolderDTO>> getAllFolders() {
        return ResponseEntity.ok(folderService.getAll());
    }

    // Lấy chi tiết 1 Folder
    @GetMapping("/{id}")
    public ResponseEntity<FolderDTO> getFolderById(@PathVariable UUID id) {
        return ResponseEntity.ok(folderService.getById(id));
    }

    // Tạo mới Folder
    @PostMapping
    public ResponseEntity<FolderDTO> createFolder(@RequestBody FolderUpsertDTO request) {
        FolderUpsertDTO createDto = new FolderUpsertDTO(
            Optional.empty(),
            request.name(),
            request.parentId()
        );
        FolderDTO created = folderService.upsert(createDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<FolderDTO> updateFolder(
        @PathVariable UUID id,
        @RequestBody FolderUpsertDTO request
    ) {

        FolderUpsertDTO updateDto = new FolderUpsertDTO(
            Optional.of(id),
            request.name(),
            request.parentId()
        );
        return ResponseEntity.ok(folderService.upsert(updateDto));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteFolder(@PathVariable UUID id) {
        folderService.delete(id);
        return ResponseEntity.noContent().build();
    }
}