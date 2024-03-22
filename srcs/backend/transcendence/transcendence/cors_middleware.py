class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.process_response(request, response)
        return response

    def process_response(self, request, response):
        response["Access-Control-Allow-Origin"] = "https://localhost"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE, PUT"
        response["Access-Control-Allow-Headers"] = "Content-Type, Accept, X-CSRFToken, Location"
        response["Access-Control-Expose-Headers"] = "Location"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
