# نشر mcp-gateway على PyPI

## الملفات الجاهزة

```
dist/
├── mcp_gateway-1.0.0-py3-none-any.whl   ← الـ wheel (للنشر)
└── mcp-gateway-1.0.0.tar.gz             ← الـ source dist (للنشر)
```

## خطوات النشر

### 1. إنشاء حساب على PyPI
- اذهب إلى https://pypi.org/account/register/
- فعّل الـ 2FA

### 2. إنشاء API Token
- https://pypi.org/manage/account/token/
- احفظ الـ token (بيبدأ بـ `pypi-`)

### 3. تثبيت twine (مرة واحدة)
```bash
pip install twine
```

### 4. رفع الـ package
```bash
twine upload dist/*
```
- Username: `__token__`
- Password: الـ token بتاعك

### 5. تأكد إنه شغال ✅
```bash
pip install mcp-gateway
mcp-gateway --help
```

## بعد النشر

الناس هتقدر تشغله بـ:
```bash
pip install mcp-gateway
mcp-gateway init     # ينشئ .env
mcp-gateway start    # يشغّل على :8000
```
