# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team:
- Members:
- Provider/model:

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> Viết 1–2 câu mô tả capability và giới hạn của agent.

**Link dùng thử:**

> URL:

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
|  |  |  |

## A3. Câu hỏi mẫu

1.
2.
3.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Không làm phần này không ảnh hưởng việc hoàn thành core lab. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in |  |  |  |
| External search + privacy boundary |  |  |  |
| Bonus: tool mới do nhóm tự xây |  |  |  |

## B6. Safety review

- Agent có bao giờ tự đoán asset ID hoặc employee ID không?
- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
- Ticket chỉ được tạo sau xác nhận rõ chưa?
- Tool result error nào cần review thủ công?

## B7. Technical reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào không thể chỉ nhìn automatic score?
- Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào?

# PHẦN C — Checkout trước khi nộp

Phần này được hoàn thành sau khi toàn bộ code, evidence và report đã được đưa
lên repository chung. Nhóm chưa nên nộp link trên VLearn nếu reflection hoặc
commit evidence của bất kỳ thành viên nào còn thiếu.

## C1. Reflection chung của nhóm

Các thành viên thảo luận và viết một reflection chung. Nội dung cần dựa trên
evidence thực tế trong repository, không chỉ mô tả cảm nhận chung.

- Mục tiêu nào của nhóm đã hoàn thành? Dẫn đến artifact hoặc run tương ứng.
- Hypothesis hoặc thay đổi nào tạo ra cải thiện rõ nhất?
- Failure quan trọng nào vẫn chưa xử lý được hoàn toàn?
- Nhóm đã phân chia, review và tích hợp công việc như thế nào?
- Nếu có thêm một vòng, nhóm sẽ ưu tiên thay đổi và kiểm chứng điều gì?

**Reflection chung của nhóm:**

> Viết reflection tại đây và dẫn link/path đến evidence liên quan.

## C2. Self-reflection của từng thành viên

Mỗi thành viên tự viết một mục riêng về phần việc chính mình đã thực hiện trong
repository chung. Không viết thay hoặc gộp nhiều thành viên vào một câu trả lời.
Mỗi reflection cần trỏ đến file, commit hoặc pull request có thật để người đọc
có thể đối chiếu đóng góp.

Sao chép mẫu dưới đây cho từng thành viên:

### Họ tên — MSSV

- **Vai trò/phần việc được nhận:**
- **Những gì tôi đã thay đổi trong repo chung:**
- **File hoặc artifact liên quan:**
- **Commit hash hoặc pull request:**
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:**
- **Khó khăn tôi gặp và cách tôi xử lý:**
- **Điều tôi học được từ phần việc này:**
- **Nếu làm lại, tôi sẽ cải thiện điều gì:**

### Vũ Minh Hiển — 2A202602692

- **Vai trò/phần việc được nhận:** Thực hiện các phiên bản v0, v1 và v2; thiết kế, điều chỉnh prompt engineering và mô tả tool dựa trên kết quả đánh giá base suite.
- **Những gì tôi đã thay đổi trong repo chung:** Tôi thiết lập baseline v0, sau đó cập nhật `system_prompt.md` và `tools.yaml` cho v1–v2. Các thay đổi gồm: không suy đoán asset/employee ID hoặc environment mơ hồ; chọn đúng `category` cho `search_kb` và `check` cho `inspect_device`; tách rõ kiểm tra dịch vụ dùng chung với kiểm tra thiết bị; áp dụng giá trị mới nhất trong multi-turn; yêu cầu xác nhận rõ ràng trước `create_ticket`; và giới hạn dữ liệu được đưa ra external search/report.
- **File hoặc artifact liên quan:** `starter_v0/artifacts/system_prompt.md`; `starter_v0/artifacts/tools.yaml`; `starter_v0/artifacts/version_log.csv`; `starter_v0/runs/v0_B_base_openrouter_20260915T185601038315.json`; `starter_v0/runs/v1_B_base_openrouter_20260915T192654152778.json`; `starter_v0/runs/v2_B_base_openrouter_20260915T193147328706.json`.
- **Commit hash hoặc pull request:** `cb61502530388c67cfa284b17717ae575833685d` — *Cap nhat prompt engineering và tools*.
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Tôi đặt các rule về định danh, routing và confirmation trực tiếp trong system prompt, đồng thời lặp lại các ràng buộc quan trọng trong description của tool. Mục tiêu là cung cấp hướng dẫn tại cả lúc model lập kế hoạch lẫn lúc chọn tool, thay vì chỉ dựa vào một lớp prompt.
- **Khó khăn tôi gặp và cách tôi xử lý:** Baseline v0 chỉ đạt 0.6667 case accuracy; các lỗi chủ yếu liên quan đến chọn tool/đối số và xử lý ngữ cảnh. Tôi dùng trace của từng run để bổ sung ràng buộc cụ thể thay vì hard-code câu hỏi eval. Kết quả base suite tăng từ 0.6667 ở v0 lên 0.8000 ở v1 và 0.9667 ở v2.
- **Điều tôi học được từ phần việc này:** Prompt engineering hiệu quả cần gắn hypothesis với metric và evidence run. Với agent có tool, việc nêu rõ điều kiện gọi tool, giá trị enum và confirmation boundary quan trọng hơn các chỉ dẫn chung chung.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Tôi sẽ tiếp tục kiểm tra các failure còn lại trên suite mở rộng/adversarial, đặc biệt là cancellation và stale confirmation, rồi đo lại cùng tiêu chí trước/sau để xác nhận các rule mới không làm giảm routing accuracy ở base suite.

Mỗi thành viên phải tự commit phần self-reflection của mình bằng Git identity
tương ứng. Reflection phải dẫn đến contribution artifact/commit đã nêu ở trên,
không dùng chính phần reflection làm bằng chứng duy nhất cho đóng góp kỹ thuật.

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [ ] `TEAMMATES.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần reflection chung của nhóm đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit self-reflection của mình.
- [ ] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [ ] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:
