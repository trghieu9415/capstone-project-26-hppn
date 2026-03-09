package io.hppn.unirag.dto.document;

import java.util.Optional;
import java.util.UUID;

public record DocumentFolder(
    UUID id,
    String name,
    Optional<DocumentFolder> parent
) {
}