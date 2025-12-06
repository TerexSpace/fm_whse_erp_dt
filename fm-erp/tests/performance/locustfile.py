import random
from locust import HttpUser, task, between

class FMERPLoadTest(HttpUser):
    """Load testing: API Gateway scalability"""
    
    wait_time = between(1, 3)  # 1-3 seconds between requests
    
    @task(3)  # Weight: 3x more common than other tasks
    def get_inventory_status(self):
        """GET /api/v1/inventory/{sku}"""
        sku = f"SKU-{random.randint(1, 500)}"
        self.client.get(f"/api/v1/inventory/{sku}")
        
    @task(2)
    def submit_order(self):
        """POST /api/v1/orders"""
        order = {
            "items": [
                {"sku": f"SKU-{random.randint(1, 500)}", "quantity": random.randint(1, 10)}
                for _ in range(random.randint(1, 5))
            ]
        }
        self.client.post("/api/v1/orders", json=order)
        
    @task(1)
    def trigger_optimization(self):
        """POST /api/v1/optimize"""
        self.client.post("/api/v1/optimize", json={"algorithm": "aqpso_bv"})
