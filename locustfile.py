import time

from locust import HttpUser, task, between

class ShopUser(HttpUser):
    # Simulates a user waiting between 1 and 3 seconds between actions
    wait_time = between(1, 3)
    
    def on_start(self):
        """
        Runs automatically when a simulated user "wakes up".
        We use this to log in/register and get a token.
        """
        # 1. Create a unique user or log in
        # (Using a hardcoded test account for simplicity, ensure it exists in your DB)
        login_data = {
            
            "phone_number":"0951504887",
            "password": "judy"
        }
        
        # We hit your login or register endpoint to get the token
        response = self.client.post("/api/login/", json=login_data)
        
        if response.status_code in [200, 201]:
            # Grab the token exactly how your backend formats it
            token = response.json().get("Token")
            # Apply the Bearer token to this user's permanent headers
            self.client.headers.update({"Authorization": f"Bearer {token}"})
        else:
            print(f"Failed to authenticate user: {response.text}")

    @task
    def  place_order_flow(self):
        """
        Simulates the user adding an item to their cart, then checking out.
        """
        # Step 1: Put something in the cart so create_order doesn't fail out immediately
        cart_payload = {
            "name": "mobile cover", # Ensure this product exists in your DB!
            "quantity": 1
        }
        self.client.post("/api/cart/store/", json=cart_payload)
        time.sleep(2)
        # Step 2: Hit the create order endpoint
        order_payload = {
            "pay_status": True,
            "location": "123 Main Street, New York, NY 10001"
        }
        
        # This tracks the actual performance of the create_order view
        self.client.post("/api/orders/create/", json=order_payload)
     