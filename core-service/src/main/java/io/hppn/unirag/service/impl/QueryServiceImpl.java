package io.hppn.unirag.service.impl;

import io.hppn.unirag.client.RagGrpcClient;
import io.hppn.unirag.persistence.repository.DocumentRepository;
import io.hppn.unirag.service.QueryService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class QueryServiceImpl implements QueryService {
    private final RagGrpcClient ragGrpcClient;
    private final DocumentRepository documentRepository;

    @Override
    public Flux<String> ask(String question, List<UUID> docIds, List<UUID> tagIds, List<UUID> folderIds) {
        HashSet<UUID> finalDocIds = new HashSet<>();
        if (docIds != null && !docIds.isEmpty()) {
            finalDocIds.addAll(docIds);
        }

        if ((folderIds != null && !folderIds.isEmpty()) || (tagIds != null && !tagIds.isEmpty())) {
            List<UUID> filteredIds = documentRepository.findIdsByFoldersAndTags(
                (folderIds != null && folderIds.isEmpty()) ? null : folderIds,
                (tagIds != null && tagIds.isEmpty()) ? null : tagIds
            );
            finalDocIds.addAll(filteredIds);
        }

        if (finalDocIds.isEmpty() && isFiltering(docIds, tagIds, folderIds)) {
            return Flux.just("Không tìm thấy tài liệu nào khớp với bộ lọc của bạn.");
        }

        return ragGrpcClient.queryRagStream(question, List.copyOf(finalDocIds));
    }

    private boolean isFiltering(List<UUID> d, List<UUID> t, List<UUID> f) {
        return (d != null && !d.isEmpty()) || (t != null && !t.isEmpty()) || (f != null && !f.isEmpty());
    }
}