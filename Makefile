all:
	docker-compose build
	docker-compose up -d
	
clean:
	docker-compose down --rmi all -v

fclean: clean
	docker system prune -f

re: fclean all

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	@echo "\n* * * * * * * * * * FRONTEND LOGS * * * * * * * * * *"
	docker logs --tail 10 frontend
	@echo "\n* * * * * * * * * * DATABASE LOGS * * * * * * * * * *"
	docker logs --tail 10 database
	@echo "\n* * * * * * * * * * BACKEND LOGS * * * * * * * * * *"
	docker logs --tail 10 backend

.PHONY: all clean fclean re up down
