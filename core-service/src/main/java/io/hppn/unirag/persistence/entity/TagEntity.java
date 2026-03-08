package io.hppn.unirag.persistence.entity;

import jakarta.persistence.*;
import lombok.*;

import java.util.UUID;

@Entity
@Table(name = "tags")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TagEntity {

    @Id
    private UUID id;

    @Column(nullable = false, unique = true, length = 50)
    private String name;

    @Column(name = "color_code", length = 7)
    private String colorCode;
}