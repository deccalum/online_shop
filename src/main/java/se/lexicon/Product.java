package se.lexicon;

public class Product {
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