package se.lexicon;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.Random;
import java.time.LocalDateTime;

public class Generators {

    private final static Random random = new Random();

    public static String[] randFirstNames = { "Simon", "Anna", "Peter", "Maria", "John", "Anna", "Peter", "Maria",
            "John",
            "Linda", "James", "Susan", "Robert", "Karen" };

    public static String[] randLastNames = { "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson" };

    public static String[] randEmailProviders = { "fmail.com", "ahooy.com", "inlook.com", "example.com",
            "notmail.com" };

    public static String[] randProductVersions = { "Pro", "Max", "Ultra", "Mini", "Plus", "Air", "Go", "Lite",
            "Prime", "Edge" };

    public static String[] randProductTypes = { "Phone", "Laptop", "Tablet", "Headphones", "Camera", "Smartwatch",
            "Speaker", "Monitor",
            "Printer", "Router" };

    public static int randID() {
        int randID = UUID.randomUUID().hashCode();
        if (randID < 0) {
            randID = -randID;
        }
        return randID;
    }

    public static String productIDGenerator() {
        return "PROD-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
    }

    public static double priceGenerator() {
        return Math.round(10 + (5000 - 10) * random.nextDouble());
    }

    public static int stockGenerator() {
        return random.nextInt(1, 21);
    }

    public static String[] productNameGenerator() {
        String ver = randProductVersions[random.nextInt(randProductVersions.length)];
        String typ = randProductTypes[random.nextInt(randProductTypes.length)];
        return new String[] { ver, typ };
    }

    public static String[] generateCustomerNameAndEmail() {
        Random rand = new Random();
        String firstName = randFirstNames[rand.nextInt(randFirstNames.length)];
        String lastName = randLastNames[rand.nextInt(randLastNames.length)];
        String provider = randEmailProviders[rand.nextInt(randEmailProviders.length)];

        String fullName = firstName + " " + lastName;
        String email = (firstName.substring(0, 1) + lastName).toLowerCase() + "@" + provider;

        return new String[] { fullName, email };
    }

    public static LocalDateTime randomOrderTimeGenerator(int orderIndex) {
        return LocalDateTime.now().plusMinutes(orderIndex * 5);
    }

}

/*
 * Ways to set random with fixed pricing
 * Order version in a list mini > lite > plus > pro etc. each with modifier
 * Same for product types
 */
/*
 * Reporting features to implement later:
 * stock simulator: return profit loss due to stock outs etc
 * restock report: products below threshold etc
 * sales report:
 */