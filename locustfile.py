from locust import HttpUser, task, between

class CloudPulseUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def home(self):
        self.client.get("/")

    @task(2)
    def health(self):
        self.client.get("/health")

    @task(1)
    def metrics(self):
        self.client.get("/metrics")