all:
	docker compose build
	docker compose up -d
	
clean:
	docker compose down --rmi all -v

fclean: clean
	docker system prune -f
	@if [ -d "pong_cli/env" ]; then rm -rf pong_cli/env; fi

re: fclean all

up:
	docker compose up -d

down:
	docker compose down

logs:
	@echo "\n* * * * * * * * * * FRONTEND LOGS * * * * * * * * * *"
	docker logs --tail 10 frontend_c
	@echo "\n* * * * * * * * * * DATABASE LOGS * * * * * * * * * *"
	docker logs --tail 10 database_c
	@echo "\n* * * * * * * * * * USER LOGS * * * * * * * * * *"
	docker logs --tail 10 transcendence_c

log:
	docker logs transcendence_c

pong_cli:
	./pong_cli/setup_cli.sh

.PHONY: all clean fclean re up down logs log pong_cli
