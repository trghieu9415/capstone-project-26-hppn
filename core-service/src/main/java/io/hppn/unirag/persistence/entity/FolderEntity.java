package io.hppn.unirag.persistence.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "folders")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FolderEntity {

    @Id
    private UUID id;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(name = "parent_id")
    private UUID parentId;

    @Column(length = 255)
    private String path;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }
}