package io.hppn.unirag.persistence.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

@Entity
@Table(name = "documents")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DocumentEntity {

    @Id
    private UUID id;

    @Column(nullable = false)
    private String title;

    @Column(name = "original_file_name", nullable = false)
    private String originalFileName;

    @Column(name = "storage_path", nullable = false, length = 500)
    private String storagePath;

    @Column(name = "file_size")
    private Long fileSize;

    @Column(name = "file_extension", length = 10)
    private String fileExtension;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "folder_id")
    private FolderEntity folder;

    @ManyToMany
    @JoinTable(
        name = "document_tags",
        joinColumns = @JoinColumn(name = "document_id"),
        inverseJoinColumns = @JoinColumn(name = "tag_id")
    )
    private Set<TagEntity> tags = new HashSet<>();

    @Enumerated(EnumType.STRING)
    @Column(name = "ai_processing_status", nullable = false)
    private AiProcessingStatus aiStatus;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        if (this.aiStatus == null) {
            this.aiStatus = AiProcessingStatus.PENDING;
        }
    }

    public enum AiProcessingStatus {
        PENDING,
        PROCESSING,
        COMPLETED,
        FAILED
    }
}