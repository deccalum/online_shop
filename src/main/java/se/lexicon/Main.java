package se.lexicon;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.Random;
import java.time.*;
import java.time.format.DateTimeFormatter;

public class Main {
    private final static Random random = new Random();

    public static void main(String[] args) {

        List<Product> products = generateProducts(10);
        System.out.println(String.format("%-15s %-20s %-15s %-10s %-10s %-10s %-6s", "PRODUCT ID", "NAME", "CATEGORY", "PRICE", "SIZE", "WEIGHT", "STOCK"));
        products.forEach(System.out::println); // #
        System.out.println();
        System.out.println();

        int orderNumber = 1;
        LocalDateTime orderTime = LocalDateTime.now();
        final int ORDER_INTERVAL_MINUTES = 5;

        while (hasStock(products)) {

            Customer customer = Customer.generateCustomer();
            Order order = purchaseOrder(customer, products, orderTime);
            System.out.println(order);
            // merge next 2 lines with order
            System.out.println(String.format("%-12s %-20s %-25s", "ID", "NAME", "EMAIL"));
            System.out.println(customer + "\n\n\n\n");
            System.out.println(String.format("%-15s %-20s %-15s %-10s %-10s %-10s %-6s", "PRODUCT ID", "NAME", "CATEGORY", "PRICE", "SIZE", "WEIGHT", "STOCK"));
            products.forEach(System.out::println); // #
            System.out.println();
            System.out.println();

            try {
                TimeUnit.SECONDS.sleep(3);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            orderNumber++;
            orderTime = orderTime.plusMinutes(ORDER_INTERVAL_MINUTES);

        }
    }

    // Simple boolean to check if any products have stock left
    private static boolean hasStock(List<Product> products) {
        return products.stream().anyMatch(p -> p.getStock() > 0); // #
    }

    // Generate and return a list of products
    private static List<Product> generateProducts(int count) {
        List<Product> list = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            list.add(new Product().generateProduct());
        }
        return list;
    }

    // Simulate a customer purchasing products
    private static Order purchaseOrder(Customer customer, List<Product> availableProducts, LocalDateTime orderTime) {
        List<OrderItem> orderItems = new ArrayList<>();
        List<Product> inStock = availableProducts.stream()
                .filter(p -> p.getStock() > 0)
                .toList();

        // If no products in stock, return empty order
        if (inStock.isEmpty()) {
            return new Order(customer, orderItems, orderTime);
        }
        
        int toBuy = random.nextInt(1, 9); // 1 to 8 products (change to odds based later)

        Map<Product, Integer> basket = new java.util.HashMap<>();
        for (int i = 0; i < toBuy; i++) {
            List<Product> currentAvailable = inStock.stream().filter(p -> p.getStock() > 0).toList();
            if (currentAvailable.isEmpty()) break;

            Product picked = currentAvailable.get(random.nextInt(currentAvailable.size()));
            basket.put(picked, basket.getOrDefault(picked, 0) + 1);
            picked.reduceStock(1);
        }
        basket.forEach((product, quantity) -> {
            orderItems.add(new OrderItem(product, quantity));
        });

        return new Order(customer, orderItems, orderTime);
    }

    // CAN BE MOVED
    public static class Customer {
        private int customerID;
        private String name;
        private String email;

        public Customer() {
        }

        public Customer(int customerID, String name, String email) {
            this.customerID = customerID;
            this.name = name;
            this.email = email;
        }

        public static Customer generateCustomer() {
            Customer customer = new Customer();
            customer.customerID = Generators.randID();
            String[] nameAndEmail = Generators.generateCustomerNameAndEmail();
            customer.name = nameAndEmail[0];
            customer.email = nameAndEmail[1];
            return customer;
        }

        public int getCustomerID() {
            return customerID;
        }

        public String getName() {
            return name;
        }

        public String getEmail() {
            return email;
        }

        public void setCustomerID(int customerID) {
            this.customerID = customerID;
        }

        public void setName(String name) {
            this.name = name;
        }

        public void setEmail(String email) {
            this.email = email;
        }

        @Override
        public String toString() {
            return String.format("%-12d %-20s %-25s", customerID, name, email);
        }
    }

    public static class Product {
        private String productID;
        private String[] product;
        private double price;
        private String category;
        private int size;
        private int weight;
        private int stock;

        public Product() {
        }

        public Product(String productID, String[] product, String category, double price, int size, int weight, int stock) {
            this.productID = productID;
            this.product = product;
            this.category = category;
            this.price = price;
            this.size = size;
            this.weight = weight;
            this.stock = stock;
        }

        public Product generateProduct() {
            this.productID = Generators.productID();
            this.product = Generators.productGenerator();

            String version = this.product[0];
            String type = this.product[1];

            this.category = Generators.productCategory(type);
            this.price = Generators.productPrice(version, type);

            int[] metrics = Generators.productMetrics(version, type);
            this.size = metrics[0];
            this.weight = metrics[1];
            
            this.stock = Generators.productStock();
            return this;
        }

        public void setPrice(double price) {
            this.price = price;
        }
        public void setCategory(String category) {
            this.category = category;
        }
        public void setSize(int size) {
            this.size = size;
        }
        public void setWeight(int weight) {
            this.weight = weight;
        }
        public void setStock(int stock) {
            this.stock = stock;
        }
        public void reduceStock(int quantity) {
            if (quantity > stock) {
                throw new IllegalArgumentException("Insufficient stock for product: " + productID);
            }
            this.stock -= quantity;
        }

        public String getProductID() {
            return productID;
        }
        public String[] getName() {
            return product;
        }
        public String getCategory() {
            return category;
        }
        public double getPrice() {
            return price;
        }
        public int getSize() {
            return size;
        }
        public int getWeight() {
            return weight;
        }
        public int getStock() {
            return stock;
        }

        @Override
        public String toString() {
            return String.format(java.util.Locale.US, "%-15s %-20s %-15s $%-9.2f %-10s %-10s %-6d",
                    productID, product[0] + " " + product[1], category, price, size + "cm", weight + "g", stock);
        }
    }

    public static class Order {
        private final String orderID;
        private final Customer customer;
        private final List<OrderItem> items;
        private final LocalDateTime orderTimeStamp;
        private final int totalSize;
        private final int totalWeight;
        private final int shipping;
        private final double subTotal;

        public Order(Customer customer, List<OrderItem> items, LocalDateTime orderTimeStamp) {
            this.orderID = "ORD-" + UUID.randomUUID().toString().substring(0, 8);
            this.customer = customer;
            this.items = new ArrayList<>(items);
            this.orderTimeStamp = orderTimeStamp;

            this.totalSize = items.stream().mapToInt(OrderItem::getSize).sum();
            this.totalWeight = items.stream().mapToInt(OrderItem::getWeight).sum();

            this.shipping = (int) Math.ceil(this.totalWeight / 1000.0) * 5;
            
            this.subTotal = items.stream().mapToDouble(OrderItem::getSubtotal).sum();
        }

        public String getOrderID() {
            return orderID;
        }
        public Customer getCustomer() {
            return customer;
        }
        public List<OrderItem> getItems() {
            return new ArrayList<>(items);
        }
        public double getTotal() {
            return subTotal + getShipping();
        }
        public LocalDateTime getOrderTimeStamp() {
            return orderTimeStamp;
        }
        public int getSize() {
            return totalSize;
        }
        public int getWeight() {
            return totalWeight;
        }
        public int getShipping() {
            if (shipping == 0) {
                return 5; // Minimum shipping cost
            }
            if (subTotal > 500) {
                return 0; // Free shipping for orders over $500
            }
            return shipping;
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd MMM HH:mm");
            sb.append(String.format("%-14s %-20s\n", orderID, orderTimeStamp.format(formatter)));
            sb.append(String.format("%-4s %-25s %-15s %-12s %-12s %-15s\n", "QT", "Product", "Category", "Unit", "SubTotal", "Packaging"));
            for (OrderItem item : items) {
                sb.append(String.format(java.util.Locale.US, "%-4d %-25s %-15s $%-11.2f $%-11.2f %-15s\n",
                        item.getQuantity(),
                        item.getProduct().getName()[0] + " " + item.getProduct().getName()[1],
                        item.getProduct().getCategory(),
                        item.getProduct().getPrice(),
                        item.getSubtotal(),
                        item.getProduct().getSize() + "cm/" + item.getProduct().getWeight() + "g"));
            }
            sb.append(String.format("\nTotal Size: %dcm, Total Weight: %dg\n", totalSize, totalWeight));
            sb.append(String.format("Shipping Cost: $%d\n", getShipping()));
            sb.append(String.format(java.util.Locale.US, "TOTAL AMOUNT: $%.2f\n", getTotal()));

            return sb.toString();
        }
    }

    public static class OrderItem {
        private final Product product;
        private final int quantity;
        private final double subtotal;
        private final int orderSize;
        private final int orderWeight;

        public OrderItem(Product product, int quantity) {
            this.product = product;
            this.quantity = quantity;
            this.subtotal = product.getPrice() * quantity;
            this.orderSize = product.getSize() * quantity;
            this.orderWeight = product.getWeight() * quantity;
        }

        public Product getProduct() {
            return product;
        }
        public int getQuantity() {
            return quantity;
        }
        public double getSubtotal() {
            return subtotal;
        }
        public int getSize() {
            return orderSize;
        }
        public int getWeight() {
            return orderWeight;
        }

        @Override
        public String toString() {
            return quantity + "x " + String.join(" ", product.getName()) +
                    " @ $" + product.getPrice() + " = $" + subtotal;
        }
    }
}

/*
 * StringBuilder in Java is a mutable sequence of characters used to efficiently
 * build and modify strings. Unlike regular String objects, which are immutable
 * (every modification creates a new object), StringBuilder allows you to
 * append, insert, delete, or modify characters without creating new objects
 * each time.
 * 
 * How it works:
 * Internally, it uses a resizable character array.
 * Methods like.append(),.insert(),.delete(),and.replace() modify the contents
 * directly.
 * It's much faster than using string concatenation (+) in loops or repeated
 * operations.
 * When you're done building the string, you can call .toString() to get the
 * final String.
 */

/*
 * forEach method in Java:
 *
 * The forEach method is used to iterate over each element in a collection (like
 * a List).
 * It takes a lambda expression or method reference as an argument and applies
 * it to every element.
 *
 * Example:
 * products.forEach(System.out::println);
 * This will call System.out.println(product) for each product in the products
 * list.
 *
 * It's a concise and readable way to perform an action on every item in a
 * collection.
 */

/*
 * Lambda expressions in Java:
 *
 * A lambda expression is a concise way to represent an anonymous function (a
 * block of code that can be passed around).
 * It is often used to implement methods of functional interfaces (interfaces
 * with a single abstract method).
 *
 * Syntax example:
 * (parameters) -> expression or { statements }
 *
 * Example with streams:
 * products.stream().anyMatch(p -> p.getStock() > 0);
 * Here, p -> p.getStock() > 0 is a lambda expression that checks if a product
 * has stock.
 *
 * Lambdas make code shorter and more readable, especially when working with
 * collections and functional-style operations.
 */

/*
 * Streams in Java:
 *
 * A Stream is a sequence of elements supporting functional-style operations on
 * collections.
 * Streams allow you to process data declaratively (what to do, not how to do
 * it).
 *
 * Common stream operations include:
 * - filter: select elements based on a condition
 * - map: transform elements
 * - forEach: perform an action for each element
 * - anyMatch, allMatch: check if any/all elements match a condition
 * - collect: gather results into a collection or value
 *
 * Example:
 * products.stream().anyMatch(p -> p.getStock() > 0);
 * This creates a stream from the products list and checks if any product has
 * stock.
 *
 * Streams make code more concise and readable, especially for complex data
 * processing.
 */