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

.PHONY: all clean fclean re up down
