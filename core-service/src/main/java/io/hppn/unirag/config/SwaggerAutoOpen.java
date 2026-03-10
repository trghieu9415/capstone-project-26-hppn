package io.hppn.unirag.config;

import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

import java.awt.*;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;

@Component
public class SwaggerAutoOpen {

    @EventListener(ApplicationReadyEvent.class)
    public void openSwaggerAfterStartup() {
        String url = "http://localhost:8080/swagger-ui/index.html";

        if (Desktop.isDesktopSupported() && !GraphicsEnvironment.isHeadless()) {
            Desktop desktop = Desktop.getDesktop();
            try {
                desktop.browse(new URI(url));
            } catch (IOException | URISyntaxException e) {
                e.printStackTrace();
            }
        } else {
            System.out.println("Swagger UI: " + url);
            Runtime runtime = Runtime.getRuntime();
            try {
                runtime.exec("rundll32 url.dll,FileProtocolHandler " + url);
            } catch (IOException e) {
                // Ignore
            }
        }
    }
}