package io.hppn.unirag.client.impl;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.StatusRuntimeException;
import io.grpc.stub.StreamObserver;
import io.hppn.unirag.client.RagGrpcClient;
import io.hppn.unirag.grpc.*;
import jakarta.annotation.PreDestroy;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Consumer;
import java.util.stream.Collectors;

@Service
public class RagGrpcClientImpl implements RagGrpcClient {

    private final ManagedChannel channel;
    private final RagEngineServiceGrpc.RagEngineServiceBlockingStub blockingStub;
    private final RagEngineServiceGrpc.RagEngineServiceStub asyncStub;

    private static final int CHUNK_SIZE = 64 * 1024;

    public RagGrpcClientImpl(
        @Value("${rag.grpc.host:localhost}") String host,
        @Value("${rag.grpc.port:50051}") int port) {

        this.channel = ManagedChannelBuilder.forAddress(host, port)
            .usePlaintext()
            .build();

        this.blockingStub = RagEngineServiceGrpc.newBlockingStub(channel);
        this.asyncStub = RagEngineServiceGrpc.newStub(channel);
    }

    @Override
    public void uploadDocument(UUID docId, String fileName, String extension, byte[] fileBytes) {
        CountDownLatch finishLatch = new CountDownLatch(1);
        AtomicReference<Throwable> errorRef = new AtomicReference<>();

        StreamObserver<UploadResponse> responseObserver = new StreamObserver<>() {
            @Override
            public void onNext(UploadResponse response) {
                if (!response.getSuccess()) {
                    errorRef.set(new RuntimeException("Python Engine error: " + response.getMessage()));
                }
            }

            @Override
            public void onError(Throwable t) {
                errorRef.set(t);
                finishLatch.countDown();
            }

            @Override
            public void onCompleted() {
                finishLatch.countDown();
            }
        };

        StreamObserver<UploadRequest> requestObserver = asyncStub.uploadDocument(responseObserver);

        try {
            String docIdStr = docId.toString();
            int offset = 0;

            while (offset < fileBytes.length) {
                int length = Math.min(CHUNK_SIZE, fileBytes.length - offset);

                UploadRequest request = UploadRequest.newBuilder()
                    .setDocId(docIdStr)
                    .setChunkData(com.google.protobuf.ByteString.copyFrom(fileBytes, offset, length))
                    .setFileName(fileName)
                    .setExtension(extension)
                    .build();

                requestObserver.onNext(request);
                offset += length;
            }

            requestObserver.onCompleted();
            if (!finishLatch.await(1, TimeUnit.MINUTES)) {
                throw new RuntimeException("Timeout waiting for AI Engine");
            }

            if (errorRef.get() != null) {
                throw new RuntimeException("Error during gRPC processing", errorRef.get());
            }

        } catch (Exception e) {
            try {
                requestObserver.onError(e);
            } catch (Exception ignored) {
            }
            throw new RuntimeException("Failed to stream document", e);
        }
    }

    @Override
    public void deleteDocument(UUID docId) {
        try {
            DeleteRequest request = DeleteRequest.newBuilder()
                .setDocId(docId.toString())
                .build();

            DeleteResponse response = blockingStub.deleteDocument(request);
            if (!response.getSuccess()) {
                throw new RuntimeException("AI Engine failed to delete doc: " + response.getMessage());
            }
        } catch (StatusRuntimeException e) {
            throw new RuntimeException("gRPC call failed: " + e.getStatus(), e);
        }
    }

    @Override
    public Flux<String> queryRagStream(String question, List<UUID> docIds) {
        return Flux.create(sink -> {
            QueryRequest request = QueryRequest.newBuilder()
                .setQuestion(question)
                .addAllDocIds(docIds.stream().map(UUID::toString).toList())
                .build();

            asyncStub.queryRag(request, new StreamObserver<QueryResponse>() {
                @Override
                public void onNext(QueryResponse value) {
                    sink.next(value.getAnswerChunk());
                }

                @Override
                public void onError(Throwable t) {
                    sink.error(t);
                }

                @Override
                public void onCompleted() {
                    sink.complete();
                }
            });

            sink.onDispose(() -> {
            });
        });
    }

    @PreDestroy
    public void shutdown() throws InterruptedException {
        channel.shutdown().awaitTermination(5, TimeUnit.SECONDS);
    }
}