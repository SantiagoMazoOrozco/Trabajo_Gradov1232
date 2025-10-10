package org.gaia.sma.util;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.stream.Collectors;

public class Proc {
    public static void run(String[] cmd) throws IOException, InterruptedException {
        ProcessBuilder pb = new ProcessBuilder(cmd);
        pb.redirectErrorStream(true);
        Process p = pb.start();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream(), StandardCharsets.UTF_8))) {
            System.out.println("$ " + Arrays.toString(cmd));
            String output = reader.lines().collect(Collectors.joining(System.lineSeparator()));
            int code = p.waitFor();
            if (code != 0) {
                throw new RuntimeException("Process failed (" + code + "): " + Arrays.toString(cmd) + "\n" + output);
            }
            System.out.println(output);
        }
    }
}
