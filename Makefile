.PHONY: setup start run ui build stop test logs list-servers add-server remove-server build-exe help

help:
	@echo ""
	@echo "  MCP Gateway"
	@echo "  ══════════════════════════════════════"
	@echo "  make setup       ← start here (wizard)"
	@echo "  make run         ← start gateway"
	@echo "  make ui          ← start UI dev server"
	@echo "  make build       ← build UI for production"
	@echo "  make start       ← start everything (Docker)"
	@echo "  make stop        ← stop Docker"
	@echo "  make test        ← run tests"
	@echo "  make logs        ← watch audit logs live"
	@echo "  make build-exe   ← build desktop executable"
	@echo ""

setup:
	python3 setup/wizard.py

run:
	@cp -n .env.example .env 2>/dev/null || true
	uvicorn gateway.main:app --reload --port 8000

ui:
	cd ui && npm install && npm run dev

build:
	cd ui && npm install && npm run build
	@echo "UI built → gateway/static"

start:
	bash scripts/start.sh

run-qa:
	docker compose -f infra/docker-compose.yml --profile qa up --build

run-dev:
	docker compose -f infra/docker-compose.yml --profile dev up --build

run-all:
	docker compose -f infra/docker-compose.yml --profile all up --build

stop:
	docker compose -f infra/docker-compose.yml --profile all down

test:
	@bash examples/test_gateway.sh

list-servers:
	python3 cli.py list

add-server:
	@test -n "$(name)" || (echo "Usage: make add-server name=X url=Y tools=t1,t2" && exit 1)
	python3 cli.py add --name $(name) --url $(url) --tools $(tools) --desc "$(desc)"

remove-server:
	@test -n "$(name)" || (echo "Usage: make remove-server name=X" && exit 1)
	python3 cli.py remove --name $(name)

logs:
	@mkdir -p logs && touch logs/audit.jsonl
	@tail -f logs/audit.jsonl | python3 -c "import sys,json; [print(json.dumps(json.loads(l), indent=2)) for l in sys.stdin]"

build-exe:
	pip install pyinstaller pillow pystray -q
	pyinstaller mcp-gateway.spec
	@echo ""
	@echo "✅ Executable ready: dist/mcp-gateway"
