# Day 04 Lab v3 — IT Helpdesk Agent Tool Eval

## Brief

Trong lab này, nhóm xây một IT Helpdesk Agent chạy thật trên model provider.
Agent nhận yêu cầu hỗ trợ, chọn tool, truyền arguments, chạy tool trên dữ liệu
doanh nghiệp giả lập, lưu full JSON trace, rồi dùng evidence đó để tối ưu prompt
và tool declaration qua nhiều version.

Điều cần học không phải là làm chatbot trả lời trôi chảy. Mục tiêu là vòng lặp
evidence-driven:

1. Chạy baseline bằng API model thật.
2. Đọc log để tìm sai tool, sai args, thiếu hỏi lại, gọi thừa hoặc vượt boundary.
3. Sửa `artifacts/system_prompt.md` hoặc `artifacts/tools.yaml`.
4. Chạy lại, đo metric và ghi versioning.
5. Tự viết eval case cho những lỗi nhóm quan tâm.
6. Trình bày kết luận dựa trên trace thật.

Toàn bộ asset, employee, service, knowledge base và policy trong lab đều là dữ
liệu giả lập local. Không sử dụng dữ liệu thật của công ty hoặc cá nhân.

## Bối cảnh nghiệp vụ

Agent hỗ trợ nhân viên trong các tình huống như:

- kiểm tra trạng thái VPN, email, SSO, Wi-Fi hoặc printing;
- kiểm tra diagnostic snapshot của một thiết bị theo asset ID;
- tra cứu tài khoản theo employee ID;
- tìm hướng dẫn trong IT knowledge base;
- tổng hợp findings thành incident report;
- hỏi lại khi thiếu identifier;
- xác nhận trước khi tạo ticket;
- tra cứu policy IT nội bộ ở advanced track.

Agent không được yêu cầu password, MFA code, token hoặc recovery code. Mọi dữ
liệu đưa vào demo và transcript phải là dữ liệu giả lập.

## Scope bắt buộc

- Setup và chạy được bằng một model provider thật.
- Giữ ít nhất 5 tool được khai báo trong `artifacts/tools.yaml`.
- Chạy fixed base eval ở `v0`.
- Tối ưu ít nhất 3 vòng thật: `v1`, `v2`, `v3`.
- Ghi đầy đủ `artifacts/version_log.csv`.
- Viết ít nhất 1 tool mới, gồm `TOOL.md`, `tool.py`, registry và YAML declaration.
- Tự viết đúng 10 case trong `data/eval_group.json`: 5 single-turn + 5 multi-turn.
- Nộp run JSON, transcript JSON và report dựa trên evidence thật.
- Có UI chạy được; khuyến nghị Streamlit nhưng không bắt buộc framework.
- Hoàn thành `artifacts/REPORT.md`: Phần A trước demo, Phần B khi nộp.

UI là deliverable core. Tool `policy` và `create_ticket` là optional/advanced,
không được tính là tool mới của nhóm. Bonus chỉ áp dụng khi nhóm hoàn thành UI và
tự xây thêm hơn 3 tool mới.

## Tool có sẵn

Core:

- `clarify`: hỏi bổ sung hoặc xin xác nhận.
- `search_kb`: tìm troubleshooting article trong knowledge base local.
- `check_service_status`: đọc trạng thái shared service giả lập.
- `inspect_device`: đọc device inventory và diagnostic snapshot.
- `lookup_user`: đọc directory record giả lập theo employee ID.
- `format_incident_report`: format findings đã có thành markdown.

Optional/advanced:

- `policy`: tìm trong IT policy markdown nội bộ giả lập.
- `create_ticket`: tạo ticket local sau khi đã có xác nhận rõ.

Starter cố tình có system prompt và tool descriptions chưa tốt. Không sửa code
implementation chỉ để ép model pass fixed eval; hãy cải thiện interface giữa
model và tool.

## Các file quan trọng

| Path | Mục đích |
|---|---|
| `starter_v0/artifacts/system_prompt.md` | Baseline instruction cố tình có lỗi |
| `starter_v0/artifacts/tools.yaml` | Tool name, description và JSON schema |
| `starter_v0/data/eval_base.json` | Fixed eval, không được sửa nội dung kỳ vọng |
| `starter_v0/data/eval_group.json` | 10 case do nhóm tự thiết kế |
| `starter_v0/data/eval_helpdesk_extension.json` | Optional policy/ticket eval |
| `starter_v0/helpdesk_data/` | Dữ liệu helpdesk giả lập local |
| `starter_v0/company_policy/` | Policy IT giả lập local |
| `starter_v0/tools/<tool_name>/` | Implementation và `TOOL.md` |
| `starter_v0/artifacts/version_log.csv` | Hypothesis và metric theo version |
| `starter_v0/artifacts/REPORT.md` | Tài liệu demo/nộp bài |

Nếu đổi tên tool, phải sync `system_prompt.md`, `tools.yaml`, `tools/__init__.py`,
`TOOL.md`, fixed eval, team eval và report. Trong fixed eval chỉ được sửa field
tên tool để đồng bộ rename; không sửa query, expected args hoặc behavior.

## Setup

Xem [TOOL-SETUP.md](TOOL-SETUP.md). Tóm tắt Windows PowerShell:

```powershell
cd starter_v0
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
python scripts/validate_lab.py
python scripts/preflight_provider.py --provider openrouter
```

Chỉ model provider cần API key. Các helpdesk tools có sẵn dùng local mock data.

## Step 1 — Baseline v0

```powershell
cd starter_v0
python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
```

Đọc các trường:

- `summary.case_accuracy`
- `summary.tool_routing_accuracy`
- `summary.argument_accuracy`
- `summary.multiturn_accuracy`
- `summary.provider_error_cases`
- `results[*].result.failures`
- `results[*].result.observed_mismatch`
- `results[*].tool_results`

Metric chỉ có giá trị khi `provider_error_cases == 0` và `measured_cases ==
total_cases`. Tool result có error phải được review thủ công.

## Step 2 — Ba vòng cải tiến

Trong mỗi vòng, đặt một hypothesis và chỉ sửa `system_prompt.md` hoặc
`tools.yaml` để kiểm chứng. Không chạy v1/v2/v3 giống hệt nhau.

```powershell
python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
```

Ví dụ hướng phân tích, không phải đáp án:

- Khi nào request nói về shared service, khi nào nói về một asset?
- Identifier nào tuyệt đối không được tự đoán?
- Từ ngữ nào map sang `check`, `environment` hoặc `priority`?
- Khi nào một request cần hai tool?
- Khi nào phải dừng lại chờ user?
- Thông tin sửa ở turn sau có ghi đè turn trước không?

Sau mỗi run, cập nhật `artifacts/version_log.csv` bằng hash và đường dẫn run.

## Step 3 — Tool mới của nhóm

Tool mới phải giải quyết một capability chưa có. Gợi ý:

- `network_diagnostics`: kiểm tra DNS, gateway và latency từ fixture local.
- `software_catalog`: kiểm tra phiên bản phần mềm được phê duyệt.
- `room_equipment`: tra cứu thiết bị phòng họp.
- `ticket_status`: đọc trạng thái ticket giả lập.

Mỗi tool cần:

1. `tools/<name>/TOOL.md` đúng frontmatter contract.
2. `tools/<name>/tool.py` với output JSON ổn định.
3. Đăng ký trong `tools/__init__.py`.
4. Declaration và schema trong `artifacts/tools.yaml`.
5. Smoke test trực tiếp và ít nhất một team eval case.

## Step 4 — Team eval

`data/eval_group.json` phải có đúng 10 case do nhóm tự viết:

- 5 case dùng `query`;
- 5 case dùng `turns`;
- turn cuối của mỗi multi-turn phải là user turn được chấm;
- `phase` luôn là `"B"`;
- `failure_type` thuộc allowed list;
- `expect` có `tool_calls` hoặc `no_tool`;
- có `metadata.what_it_tests`.

Hai case trong `samples/eval_group.schema.example.json` chỉ minh họa schema,
không được tính vào 10 case.

```powershell
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
```

Advanced track:

```powershell
python run_eval.py --provider openrouter --version v3 --suite extension --eval-cases data/eval_helpdesk_extension.json
```

Extension có case tạo ticket local. Chỉ chạy khi nhóm hiểu confirmation boundary;
ticket được ghi vào `starter_v0/tickets/` và không cần nộp.

## Step 5 — UI và live chat

UI cần hiển thị request, final response, từng tool call + args + result/error,
version/artifact hash và transcript. Nếu dùng Streamlit, tái sử dụng
`run_model_tool_loop` trong `chat.py`, không viết agent loop thứ hai.

CLI chat:

```powershell
python chat.py --provider openrouter --version v3
```

Rehearse ít nhất 3 scenario:

1. Kiểm tra một sự cố cần status + device inspection.
2. Thiếu asset ID rồi bổ sung ở turn sau.
3. Soạn ticket, sửa priority rồi xác nhận tạo.

## Bằng chứng và nộp bài

Nộp `starter_v0/` với artifacts, đúng 10 group cases, run JSON, transcript JSON,
tool mới, UI và dependency. Không nộp `.env`, key, `.venv`, cache hoặc tickets.

Không dùng password, token, MFA code hoặc dữ liệu thật trong query, log, report,
screenshot hay demo public.

## Checkpoints gợi ý — 09:00–13:00

1. 09:00–09:15: kickoff, đọc tool/data/policy.
2. 09:15–09:40: setup, validate local, provider preflight.
3. 09:40–10:15: baseline v0, đọc failed trace, dựng UI skeleton.
4. 10:15–10:50: v1 và tool mới.
5. 10:50–11:05: nghỉ.
6. 11:05–11:30: 10 group cases, v2, Report A, rehearsal.
7. 11:30–12:15: showdown và challenge chéo.
8. 12:15–12:40: v3, Report B, final gate.
9. 12:40–13:00: recap.
