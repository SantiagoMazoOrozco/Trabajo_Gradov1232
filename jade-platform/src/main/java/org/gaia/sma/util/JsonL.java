package org.gaia.sma.util;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;

public class JsonL {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    public static synchronized void append(Path jsonlPath, Map<String, Object> event) throws IOException {
        if (jsonlPath.getParent() != null) Files.createDirectories(jsonlPath.getParent());
        String line = MAPPER.writeValueAsString(event);
        try (BufferedWriter w = Files.newBufferedWriter(jsonlPath, StandardCharsets.UTF_8,
                java.nio.file.StandardOpenOption.CREATE,
                java.nio.file.StandardOpenOption.APPEND)) {
            w.write(line);
            w.newLine();
        }
    }
}
