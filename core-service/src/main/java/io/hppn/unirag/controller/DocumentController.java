package io.hppn.unirag.controller;

import io.hppn.unirag.dto.document.DocumentDTO;
import io.hppn.unirag.dto.document.request.DocumentUpsertDTO;
import io.hppn.unirag.service.DocumentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/api/documents")
@RequiredArgsConstructor
public class DocumentController {

    private final DocumentService documentService;

    @GetMapping("/{id}")
    public ResponseEntity<DocumentDTO> getDocumentById(@PathVariable UUID id) {
        return ResponseEntity.ok(documentService.getById(id));
    }

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<DocumentDTO> createDocument(
        @RequestParam("file") MultipartFile file,
        @ModelAttribute DocumentUpsertDTO request) {
        try {
            DocumentUpsertDTO createDto = new DocumentUpsertDTO(
                Optional.empty(),
                request.folder(),
                request.tags(),
                request.name(),
                request.extension()
            );

            byte[] fileBytes = file.getBytes();
            DocumentDTO created = documentService.upsert(createDto, fileBytes);
            return ResponseEntity.status(HttpStatus.CREATED).body(created);
        } catch (IOException e) {
            throw new RuntimeException("Lỗi khi đọc file upload: " + e.getMessage());
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<DocumentDTO> updateDocumentMetadata(
        @PathVariable UUID id,
        @RequestBody DocumentUpsertDTO request) {

        DocumentUpsertDTO updateDto = new DocumentUpsertDTO(
            Optional.of(id),
            request.folder(),
            request.tags(),
            request.name(),
            request.extension()
        );

        DocumentDTO updated = documentService.upsert(updateDto, null);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDocument(@PathVariable UUID id) {
        documentService.delete(id);
        return ResponseEntity.noContent().build();
    }
}