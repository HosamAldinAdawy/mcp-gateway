# MCP Gateway — Quickstart

أسرع طريقة تشغل الـ gateway وتجربه في 5 دقايق.

## الخطوة الأولى — Clone

```bash
git clone https://github.com/HosamAldinAdawy/mcp-gateway.git
cd mcp-gateway
pip install -r requirements.txt
```

## الخطوة التانية — Setup Wizard

```bash
python setup/wizard.py
```

الـ wizard هيسألك:
- إيه الـ templates اللي محتاجها
- هتستخدمه مع إيه (Claude, Cursor, Python...)
- هيولد الـ API key تلقائي

## الخطوة التالتة — شغل

```bash
make run
```

خلاص! الـ gateway شغال على `http://localhost:8000`

---

## تجربة سريعة

```bash
# اعمل .env الأول
cp .env.example .env
# عدّل MCP_API_KEYS بـ key بتاعك

# شغّل
make run

# اختبر
curl http://localhost:8000/health

# اتصل بـ tool
curl -X POST http://localhost:8000/v1/call \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"server": "echo-server", "tool": "echo", "arguments": {"message": "يا هلا!"}}'
```

---

## الخطوة الجاية

- أضف templates: `make add-server --template jira`
- شوف الـ servers: `make list-servers`
- تابع الـ logs: `make logs`
