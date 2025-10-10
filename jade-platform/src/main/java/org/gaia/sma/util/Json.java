package org.gaia.sma.util;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;

public class Json {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    public static void write(Path path, Map<String, Object> data) throws IOException {
        if (path.getParent() != null) Files.createDirectories(path.getParent());
        MAPPER.writerWithDefaultPrettyPrinter().writeValue(path.toFile(), data);
    }

    public static Map<String, Object> read(Path path) throws IOException {
        return MAPPER.readValue(path.toFile(), new TypeReference<Map<String, Object>>() {});
    }
}
