package org.gaia.sma;

import org.gaia.sma.agents.CoordinatorAgent;

public class App {
    public static void main(String[] args) throws Exception {
        // Simple entry point: run a single coordinator that orchestrates the Python CLI bridge.
        // Controls via system properties or env: EXPERIMENT_ID and SEED
        String exp = System.getProperty("experimentId");
        if (exp == null || exp.isBlank()) exp = System.getenv("EXPERIMENT_ID");
        if (exp == null || exp.isBlank()) exp = "exp_jade_demo";

        String seedStr = System.getProperty("seed");
        if (seedStr == null || seedStr.isBlank()) seedStr = System.getenv("SEED");
        int seed;
        try {
            seed = seedStr != null ? Integer.parseInt(seedStr) : 42;
        } catch (NumberFormatException nfe) {
            seed = 42;
        }

        CoordinatorAgent coordinator = new CoordinatorAgent();
        coordinator.runOne(exp, seed);
    }
}
