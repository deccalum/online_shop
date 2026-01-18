import com.google.gson.JsonParser;

// Read optimization results
String json = Files.readString(Paths.get("optimization_results.json"));
JsonObject results = JsonParser.parseString(json).getAsJsonObject();

double netProfit = results.get("objective_value").getAsDouble();
JsonObject orders = results.getAsJsonObject("purchase_orders");

for (String month : orders.keySet()) {
    System.out.println("Month " + month + ": " + orders.get(month));
}