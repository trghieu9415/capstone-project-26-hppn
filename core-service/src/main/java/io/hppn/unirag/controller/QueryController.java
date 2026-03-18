package io.hppn.unirag.controller;

import io.hppn.unirag.dto.query.QueryRequestDTO;
import io.hppn.unirag.service.QueryService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

@RestController
@RequestMapping("/api/query")
@RequiredArgsConstructor
public class QueryController {

    private final QueryService queryService;

    @PostMapping(value = "/ask")
    public String askQuery(@RequestBody QueryRequestDTO dto) {
        System.out.println("--- Nhận câu hỏi: " + dto.question());
        return queryService.ask(dto.question(), dto.docIds(), dto.tagIds(), dto.folderIds());
    }

    @PostMapping(value = "/ask/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> askStream(@RequestBody QueryRequestDTO dto) {
        System.out.println("--- Nhận câu hỏi: " + dto.question());

        return queryService.askStream(
            dto.question(),
            dto.docIds(),
            dto.tagIds(),
            dto.folderIds()
        ).onErrorResume(e -> {
            System.err.println("Lỗi stream: " + e.getMessage());
            return Flux.just("\n[Hệ thống]: Rất tiếc, AI Engine đang gặp sự cố. Vui lòng thử lại sau.");
        });
    }
}