# IT Helpdesk Lab — Setup and Validation

Tài liệu dành cho `starter_v0/`. Core helpdesk tools dùng dữ liệu local giả lập.
Model provider cần một API key; optional external device search cần Tavily key.

## 1. Cài môi trường

Windows PowerShell:

```powershell
cd starter_v0
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

macOS/Linux:

```bash
cd starter_v0
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
```

Không ghi đè `.env` đã có và không nộp file này.

## 2. Chọn model provider

Điền đúng một key vào `.env`. OpenRouter là lựa chọn khuyến nghị:

```text
OPENROUTER_API_KEY=...
```

Hoặc dùng `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` hay `GEMINI_API_KEY` và đổi
`--provider` tương ứng trong mọi command.

## 3. Validate local trước khi dùng API

```powershell
python scripts/validate_lab.py
```

Script kiểm tra JSON/YAML, registry/declaration, toàn bộ expected tool trong base
và extension, contract của tool local, confirmation boundary và evaluator. Đây
là test deterministic, không tiêu quota.

Có thể chạy unit test chi tiết:

```powershell
python -m unittest discover -s tests -v
```

## 4. Provider preflight

```powershell
python scripts/preflight_provider.py --provider openrouter
```

PASS khi provider trả structured tool call. Preflight không chấm đúng/sai toàn
bộ routing; base eval mới thực hiện việc đó.

## 5. Smoke test từng tool

Chạy từ `starter_v0/`:

```powershell
python -c "from tools import TOOL_FUNCTIONS as T; print(T['check_service_status']('vpn', 'production'))"
python -c "from tools import TOOL_FUNCTIONS as T; print(T['inspect_device']('LT-204', 'vpn'))"
python -c "from tools import TOOL_FUNCTIONS as T; print(T['lookup_user']('EMP-1003'))"
python -c "from tools import TOOL_FUNCTIONS as T; print(T['search_kb']('Outlook Windows 11', 'email', 1))"
python -c "from tools import TOOL_FUNCTIONS as T; print(T['policy']('xác nhận tạo ticket', 'ticketing', 1))"
python -c "from tools import TOOL_FUNCTIONS as T; print(T['create_ticket']('dry run', 'low', 'LT-204', False))"
```

Lệnh cuối phải trả `needs_confirmation` và không tạo file.

## 6. Optional external device search

`search_device_info` gọi Tavily Search API để tìm trang specs, driver, support
hoặc compatibility theo hãng/model công khai.

Tạo key theo [Tavily Search documentation](https://docs.tavily.com/documentation/api-reference/endpoint/search),
sau đó thêm vào `.env`:

```text
TAVILY_API_KEY=tvly-...
```

Smoke test:

```powershell
python -c "from pathlib import Path; from env_loader import load_lab_env; load_lab_env(Path.cwd()); from tools import TOOL_FUNCTIONS as T; r=T['search_device_info']('Lenovo','ThinkPad T14 Gen 4','drivers',2); print({'error':r.get('error'),'item_count':len(r.get('items') or []),'domains':r.get('official_domains')})"
```

Tool chỉ được nhận manufacturer/model công khai. Không truyền asset ID, employee
ID, serial number, hostname, diagnostic log hoặc credential ra external API.

## 7. Tool mới của nhóm

Quicktest implementation trực tiếp trước khi đưa cho model:

```powershell
python -c "from tools import TOOL_FUNCTIONS as T; r=T['YOUR_TOOL_NAME'](**{'YOUR_ARG':'DEMO_VALUE'}); print({'error':r.get('error') if isinstance(r,dict) else None,'type':type(r).__name__})"
```

PASS khi registry tìm thấy tool, args đúng contract, không có error và output là
dữ liệu giả lập mong đợi. Action tool phải test ở dry-run hoặc `confirmed=False`.

## 8. Chạy eval

```powershell
python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
```

Không sửa fixed base cases để tăng điểm. Provider error hoặc tool result error
phải được ghi nhận, không được xóa khỏi evidence.

## 9. UI

Nếu dùng Streamlit, thêm `streamlit>=1.30.0` vào `requirements.txt`, tạo `app.py`
và tái sử dụng `run_model_tool_loop` trong `chat.py`.

```powershell
streamlit run app.py
```

UI phải hiển thị request/response, tool trace, args, result/error, version/hash
và transcript. Chỉ dùng fixture giả lập; không nhập credential hoặc dữ liệu thật.

## Final gate

- `python scripts/validate_lab.py` pass;
- provider preflight pass;
- base/group eval không có provider error;
- tool mới có smoke test và eval evidence;
- UI chạy và có tool trace;
- report dựa trên đúng run/transcript;
- `.env`, keys, `.venv`, cache và `tickets/` không nằm trong bài nộp.
