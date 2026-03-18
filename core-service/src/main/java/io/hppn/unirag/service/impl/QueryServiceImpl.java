package io.hppn.unirag.service.impl;

import io.hppn.unirag.client.RagGrpcClient;
import io.hppn.unirag.persistence.repository.DocumentRepository;
import io.hppn.unirag.service.QueryService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class QueryServiceImpl implements QueryService {
    private final RagGrpcClient ragGrpcClient;
    private final DocumentRepository documentRepository;

    @Override
    public String ask(String question, List<UUID> docIds, List<UUID> tagIds, List<UUID> folderIds) {
        List<UUID> finalDocIds = resolveDocumentIds(docIds, tagIds, folderIds);
        return ragGrpcClient.queryRag(question, finalDocIds);
    }

    @Override
    public Flux<String> askStream(String question, List<UUID> docIds, List<UUID> tagIds, List<UUID> folderIds) {
        List<UUID> finalDocIds = resolveDocumentIds(docIds, tagIds, folderIds);

        if (finalDocIds.isEmpty() && isFiltering(docIds, tagIds, folderIds)) {
            return Flux.just("Không tìm thấy tài liệu nào khớp với bộ lọc của bạn.");
        }

        return ragGrpcClient.queryRagStream(question, finalDocIds);
    }


    private List<UUID> resolveDocumentIds(List<UUID> docIds, List<UUID> tagIds, List<UUID> folderIds) {
        Set<UUID> finalDocIds = new HashSet<>();

        if (!isNullOrEmpty(docIds)) {
            finalDocIds.addAll(docIds);
        }

        if (!isNullOrEmpty(folderIds) || !isNullOrEmpty(tagIds)) {
            List<UUID> filteredIds = documentRepository.findIdsByFoldersAndTags(
                isNullOrEmpty(folderIds) ? null : folderIds,
                isNullOrEmpty(tagIds) ? null : tagIds
            );

            if (filteredIds != null) {
                finalDocIds.addAll(filteredIds);
            }
        }

        return List.copyOf(finalDocIds);
    }

    private boolean isFiltering(List<UUID> docIds, List<UUID> tagIds, List<UUID> folderIds) {
        return !isNullOrEmpty(docIds) || !isNullOrEmpty(tagIds) || !isNullOrEmpty(folderIds);
    }

    private boolean isNullOrEmpty(List<?> list) {
        return list == null || list.isEmpty();
    }
}