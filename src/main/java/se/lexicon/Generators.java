package se.lexicon;

import java.util.Arrays;
import java.util.UUID;
import java.util.Random;
import java.time.LocalDateTime;

public class Generators {

    private final static Random random = new Random();

    public static String[] firstNames = { "Simon", "Anna", "Peter", "Maria", "John", "Anna", "Peter", "Maria",
            "John",
            "Linda", "James", "Susan", "Robert", "Karen" };

    public static String[] lastNames = { "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson" };

    public static String[] randEmailProviders = { "@fmail.com", "@ahooy.com", "@inlook.com", "@example.com",
            "@notmail.com" };

    private static final Object[][] productVersion = {
            { "Lite", 0.6 },
            { "Mini", 0.7 },
            { "Go", 0.8 },
            { "Air", 0.85 },
            { "Plus", 1.0 },
            { "Prime", 1.2 },
            { "Pro", 1.3 },
            { "Max", 1.5 },
            { "Ultra", 1.8 },
            { "Edge", 1.9 }
    };

    private static final Object[][] productType = {
            { "Phone", 1.0, "Handhelds" },
            { "Laptop", 7.5, "Computers" },
            { "Desktop", 10.0, "Computers" },
            { "Tablet", 5.0, "Handhelds" },
            { "Headphones", 0.8, "Audio" },
            { "Earbuds", 0.5, "Audio" },
            { "Camera", 1.4, "Imaging" },
            { "Smart TV", 3.0, "Entertainment" },
            { "Smartwatch", 0.9, "Wearables" },
            { "Speaker", 0.7, "Audio" },
            { "Monitor", 5.0, "Computers" },
            { "Printer", 1.1, "Computers" },
            { "Router", 0.6, "Networking" }
    };

    public static int randID() {
        int randID = UUID.randomUUID().hashCode();
        if (randID < 0) {
            randID = -randID;
        }
        return randID;
    }

    public static String[] generateCustomerNameAndEmail() {
        String firstName = firstNames[random.nextInt(firstNames.length)];
        String lastName = lastNames[random.nextInt(lastNames.length)];
        String provider = randEmailProviders[random.nextInt(randEmailProviders.length)];

        String fullName = firstName + " " + lastName;
        String email = (firstName.substring(0, 1) + lastName).toLowerCase() + provider;

        return new String[] { fullName, email };
    }

    // PRODUCT GENERATORS

    public static String productID() {
        return "PROD-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
    }

    public static String[] productGenerator() {
        Object[] verRow = productVersion[random.nextInt(productVersion.length)];
        Object[] prodRow = productType[random.nextInt(productType.length)];

        String version = verRow[0].toString();
        String type = prodRow[0].toString();
        String category = prodRow[2].toString();

        // Return version, type, and category to match caller expectations
        return new String[] { version, type, category };
    }

    public static double productPrice(String version, String type) {
        // Base price range: $50-$80
        double basePrice = 50 + (80 - 50) * random.nextDouble();

        // Resolve modifiers by provided names (fallback to 1.0 if not found)
        double vMod = 1.0;
        for (Object[] v : productVersion) {
            if (v[0].toString().equals(version)) {
                vMod = (double) v[1];
                break;
            }
        }
        double tMod = 1.0;
        for (Object[] p : productType) {
            if (p[0].toString().equals(type)) {
                tMod = (double) p[1];
                break;
            }
        }
        // Small random variation
        double rMod = 0.90 + (random.nextDouble() * 0.10);
        double finalPrice = basePrice * vMod * tMod * rMod;
        // Round to 2 decimal places
        return Math.round(finalPrice * 100.0) / 100.0;
    }

    public static String productCategory(String category) {
        for (Object[] p : productType) {
            if (p[0].toString().equals(category)) {
                return p[2].toString();
            }
        }
        return "Unknown";
    }

    public static int[] productMetrics(String version, String type) {
        double vMod = 1.0, tMod = 1.0;
        for (Object[] v : productVersion) if (v[0].equals(version)) vMod = (double) v[1];
        for (Object[] t : productType) if (t[0].equals(type)) tMod = (double) t[1];

        int sizeSquared = (int) Math.pow(10 * tMod, 2);
        int weight = (int) (500 * vMod * tMod * random.nextDouble());
        return new int[] { sizeSquared, weight };
    }

    /*
    public static int[] ratingGenerator() {
        int ratingsCount = random.nextInt(1, 501); // 1 to 500 ratings
        int averageRating = random.nextInt(1, 6); // 1 to 5 stars
        return new int[] { averageRating, ratingsCount };
    }
    */

    public static int productStock() {
        return random.nextInt(1, 21);
    }

    public static LocalDateTime randomOrderTimeGenerator(int orderIndex) {
        return LocalDateTime.now().plusMinutes(orderIndex * 5);
    }

        // not used. Kept for reference
    public static String formatVersionModifiers() {
        return Arrays.stream(productVersion) // gets all key-valie pairs as a stream
                .map(e -> e[0] + ": " + e[1]) // maps each entry to a string "key: value"
                .reduce((a, b) -> a + ", " + b) // reduces the stream to a single string, concatenating with ", "
                .orElse(""); // returns the resulting string or an empty string if the map is empty
    }
}





    /*
     * ENUM EXAMPLE:
     * public enum ProductVersion {
     * LITE(0.6),
     * MINI(0.7),
     * GO(0.8),
     * ULTRA(1.8),
     * PRO(1.3);
     * 
     * private final double multiplier;
     * ProductVersion(double multiplier) { this.multiplier = multiplier; }
     * public double getMultiplier() { return multiplier; }
     * }
     */