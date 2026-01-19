
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

public class FileImporter {

    private static final Path CONFIG_PATH = Paths.get("config", "config.cfg");

    /**
     * Resolve the filtered catalog file path defined in config/config.cfg.
     */
    public static Path getFilteredCatalogFilePath() throws IOException {
        return resolveFilteredCatalogFilePath(CONFIG_PATH);
    }

    private static Path resolveFilteredCatalogFilePath(Path configPath) throws IOException {
        if (!Files.exists(configPath)) {
            throw new IOException("Config file not found: " + configPath.toAbsolutePath());
        }

        String filteredCatalog = readConfigValue(configPath, "filtered_catalog_file")
                .orElseThrow(() -> new IOException("filtered_catalog_file not defined in " + configPath));

        Path baseDir = configPath.getParent();
        return (baseDir == null ? Paths.get("") : baseDir).resolve(filteredCatalog).normalize();
    }

    private static Optional<String> readConfigValue(Path configPath, String key) throws IOException {
        String prefixEq = key + "=";
        String prefixSpaceEq = key + " =";

        return Files.lines(configPath)
                .map(String::trim)
                .filter(line -> !line.isEmpty())
                .filter(line -> !line.startsWith("#"))
                .filter(line -> !line.startsWith("["))
                .filter(line -> line.startsWith(prefixEq) || line.startsWith(prefixSpaceEq))
                .map(line -> line.split("=", 2)[1].trim())
                .findFirst();
    }
}
