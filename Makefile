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
	docker logs --tail 10 frontend_c
	@echo "\n* * * * * * * * * * DATABASE LOGS * * * * * * * * * *"
	docker logs --tail 10 database_c
	@echo "\n* * * * * * * * * * PONG LOGS * * * * * * * * * *"
	docker logs --tail 10 pong_service_c

.PHONY: all clean fclean re up down
