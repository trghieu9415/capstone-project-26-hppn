package io.hppn.unirag.service;

import reactor.core.publisher.Flux;

import java.util.List;
import java.util.UUID;

public interface QueryService {
    String ask(String question, List<UUID> docIds, List<UUID> tagIds, List<UUID> folderIds);

    Flux<String> askStream(String question, List<UUID> docIds, List<UUID> tagIds, List<UUID> folderIds);
}