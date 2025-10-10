package org.gaia.sma.agents;

import org.gaia.sma.util.Json;
import org.gaia.sma.util.JsonL;
import org.gaia.sma.util.Proc;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

public class CoordinatorAgent {
    private final String python;

    public CoordinatorAgent() {
        String py = System.getenv("PYTHON_CMD");
        this.python = (py != null && !py.isBlank()) ? py : "python";
    }

    public void runOne(String experimentId, int seed) throws Exception {
        // Resolve workspace root (jade-platform/..)
        Path root = Paths.get("").toAbsolutePath().getParent();
        Path dataDir = root.resolve("data");
        Path pyAnalysis = root.resolve("python-analysis");

        // Ensure results dir
        Path expDir = dataDir.resolve(Path.of("results", experimentId));
        Files.createDirectories(expDir);
        Path logsDir = expDir.resolve("logs");
        Files.createDirectories(logsDir);
        Path evLog = logsDir.resolve("events_jade.jsonl");

        // Step 1: preprocess via CLI bridge
        JsonL.append(evLog, Map.of("ts", Instant.now().toString(), "stage", "PREPROCESS", "event", "start", "experimentId", experimentId, "seed", seed));
        Map<String, Object> prep = retry(() -> callPreprocess(pyAnalysis, dataDir, experimentId, seed), 2, evLog, "PREPROCESS", experimentId, seed);
        JsonL.append(evLog, Map.of("ts", Instant.now().toString(), "stage", "PREPROCESS", "event", "success", "experimentId", experimentId));
        // Step 2: train RF
        JsonL.append(evLog, Map.of("ts", Instant.now().toString(), "stage", "TRAIN_RF", "event", "start", "experimentId", experimentId));
        Map<String, Object> trainRF = retry(() -> callTrain(pyAnalysis, dataDir, experimentId, seed, "RF", prep), 2, evLog, "TRAIN_RF", experimentId, seed);
        JsonL.append(evLog, Map.of("ts", Instant.now().toString(), "stage", "TRAIN_RF", "event", "success", "experimentId", experimentId));
        // Step 3: eval RF
        JsonL.append(evLog, Map.of("ts", Instant.now().toString(), "stage", "EVAL_RF", "event", "start", "experimentId", experimentId));
        Map<String, Object> evalRF = retry(() -> callEvaluate(pyAnalysis, dataDir, experimentId, "rf", trainRF), 2, evLog, "EVAL_RF", experimentId, seed);
        JsonL.append(evLog, Map.of("ts", Instant.now().toString(), "stage", "EVAL_RF", "event", "success", "experimentId", experimentId));
        // Step 4: train SVM
        JsonL.append(evLog, Map.of("ts", Instant.now().toString(), "stage", "TRAIN_SVM", "event", "start", "experimentId", experimentId));
        Map<String, Object> trainSVM = retry(() -> callTrain(pyAnalysis, dataDir, experimentId, seed, "SVM", prep), 2, evLog, "TRAIN_SVM", experimentId, seed);
        JsonL.append(evLog, Map.of("ts", Instant.now().toString(), "stage", "TRAIN_SVM", "event", "success", "experimentId", experimentId));
        // Step 5: eval SVM
        JsonL.append(evLog, Map.of("ts", Instant.now().toString(), "stage", "EVAL_SVM", "event", "start", "experimentId", experimentId));
        Map<String, Object> evalSVM = retry(() -> callEvaluate(pyAnalysis, dataDir, experimentId, "svm", trainSVM), 2, evLog, "EVAL_SVM", experimentId, seed);
        JsonL.append(evLog, Map.of("ts", Instant.now().toString(), "stage", "EVAL_SVM", "event", "success", "experimentId", experimentId));

        // Write a minimal meta.json to mark this as a JADE-orchestrated experiment
        Map<String, Object> meta = new HashMap<>();
        meta.put("experimentId", experimentId);
        meta.put("group", "treatment");
        meta.put("seed", seed);
        meta.put("orchestrator", "java-cli");
        meta.put("created_utc", Instant.now().toString());
        Json.write(expDir.resolve("meta.json"), meta);
    }

    interface ThrowingSupplier<T> { T get() throws Exception; }

    private <T> T retry(ThrowingSupplier<T> op, int retries, Path evLog, String stage, String experimentId, int seed) throws Exception {
        int attempts = 0;
        Exception last = null;
        while (attempts <= retries) {
            try {
                return op.get();
            } catch (Exception ex) {
                last = ex;
                attempts++;
                JsonL.append(evLog, Map.of(
                        "ts", Instant.now().toString(),
                        "stage", stage,
                        "event", "error",
                        "experimentId", experimentId,
                        "seed", seed,
                        "attempt", attempts,
                        "message", ex.getMessage()
                ));
                if (attempts > retries) break;
                Thread.sleep(500L * attempts);
            }
        }
        throw last;
    }

    Map<String, Object> callPreprocess(Path pyAnalysis, Path dataDir, String experimentId, int seed) throws Exception {
        String prepRefPath = dataDir.resolve(Path.of("results", experimentId, "prepRef.json")).toString();
    String[] cmd = new String[]{
        this.python, pyAnalysis.resolve("agent_cli.py").toString(), "preprocess",
                "--experiment-id", experimentId,
                "--data", dataDir.resolve("raw/synthetic_classification.csv").toString(),
                "--scale", "true",
                "--test-size", "0.2",
                "--seed", Integer.toString(seed),
                "--out", prepRefPath
        };
        Proc.run(cmd);
        return Json.read(Path.of(prepRefPath));
    }

    Map<String, Object> callTrain(Path pyAnalysis, Path dataDir, String experimentId, int seed, String algo, Map<String, Object> prepRef) throws Exception {
        // Save prepRef to a temp file for CLI
        String prepRefPath = dataDir.resolve(Path.of("results", experimentId, "prepRef.json")).toString();
        Json.write(Path.of(prepRefPath), prepRef);
        String outPath = dataDir.resolve(Path.of("results", experimentId, "train_" + algo.toLowerCase() + ".json")).toString();
    String[] cmd = new String[]{
        this.python, pyAnalysis.resolve("agent_cli.py").toString(), "train",
                "--experiment-id", experimentId,
                "--algo", algo,
                "--seed", Integer.toString(seed),
                "--prep-ref-file", prepRefPath,
                "--out", outPath
        };
        Proc.run(cmd);
        return Json.read(Path.of(outPath));
    }

    Map<String, Object> callEvaluate(Path pyAnalysis, Path dataDir, String experimentId, String tag, Map<String, Object> trainResult) throws Exception {
        String modelOutPath = dataDir.resolve(Path.of("results", experimentId, "modelRef_for_eval_" + tag + ".json")).toString();
        Json.write(Path.of(modelOutPath), trainResult);
        String outPath = dataDir.resolve(Path.of("results", experimentId, "eval_" + tag + ".json")).toString();
    String[] cmd = new String[]{
        this.python, pyAnalysis.resolve("agent_cli.py").toString(), "evaluate",
                "--experiment-id", experimentId,
                "--model-ref-file", modelOutPath,
                "--metrics", "accuracy", "f1",
                "--confusion-matrix", "true",
                "--out", outPath
        };
        Proc.run(cmd);
        return Json.read(Path.of(outPath));
    }
}
