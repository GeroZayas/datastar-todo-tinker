run:
	uvicorn todo:app --reload

git:
	git add -A && \
	printf "message: "; \
	read MESSAGE; \
	git commit -m "$$MESSAGE" && \
	git push