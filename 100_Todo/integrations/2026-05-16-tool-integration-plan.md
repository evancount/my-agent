---
created: 2026-05-16
status: in-progress
source: pro-kit 03「外部工具整合包 by 雷小蒙」
---

# 外部工具整合計畫（2026-05-16）

> 這份計畫是「外部工具整合包」訪談後產出的，列出所有你打算接到 Claude Code 的工具。
> **執行方式**：有空的時候打開這份文件跟 AI 說：「幫我挑一個來裝」，AI 會用網路搜尋查當下最新的整合方式，一步一步帶你裝，完成後把對應的 checklist 打勾。

## 決策原則速查

在選每個工具的路線前，優先順序是：

1. 🥇 **CLI**（`gh`、`gws-cli`、官方 CLI）— 不吃 context、最穩定
2. 🥈 **REST API + `.env`**（curl / Python requests）— 彈性最高、可精準控制
3. 🥉 **MCP**（`~/.claude.json` 的 `mcpServers`）— 只有 CLI + API 都不行時才用
4. 🔒 **瀏覽器控制**（Chrome DevTools MCP / Playwright）— 真的沒 API 才走這條

每個工具的「建議路線」欄位是 AI 初步判斷，實際執行時會再用網路搜尋確認當下最新的最佳做法。

---

## 工具清單

### 🟢 GitHub — 已整合

- **用途**：程式碼管理、repo 操作
- **實際路線**：CLI（`gh`）
- **狀態**：已在 pro-kit 01 時安裝 gh CLI v2.92.0，已登入為 evancount
- **安裝 checklist**：
  - [x] 安裝 gh CLI
  - [x] 完成 auth login
  - [x] 驗證 `gh auth status` 正常
- **備註**：gh 安裝在 `/tmp/gh_install/gh_2.92.0_macOS_arm64/bin/gh`，建議之後用 brew 正式安裝

### 🟡 Gmail — 尚未整合

- **用途**：讀信、建草稿、搜尋信件
- **建議路線**：MCP（Gmail MCP 是目前最成熟的方案，因為 OAuth 流程需要 MCP 代理）
- **執行時要查的事情**：
  - [ ] Gmail MCP 目前官方推薦的套件是哪個？（搜尋 `Gmail Claude Code MCP 2026`）
  - [ ] OAuth 授權流程需要什麼前置作業？（Google Cloud Console 設定）
  - [ ] 有沒有比 MCP 更新/更穩的方案？（例如 gws-cli）
- **安裝 checklist**：
  - [ ] 取得 OAuth 憑證（Google Cloud Console）
  - [ ] 依 AI 查到的最新步驟安裝
  - [ ] 跑驗證：「幫我看最近 3 封信的主旨」
  - [ ] 回來打勾 + 在「備註」欄記下任何踩坑
- **備註**：（執行完畢後寫這裡）

### 🟡 Google Calendar — 尚未整合

- **用途**：查行程、排時間、建活動
- **建議路線**：MCP（跟 Gmail 通常可以共用同一組 Google OAuth 憑證）
- **執行時要查的事情**：
  - [ ] Google Calendar MCP 目前最穩定的套件？
  - [ ] 能不能跟 Gmail MCP 共用 OAuth token？
  - [ ] 有沒有 CLI 替代方案（gws-cli 或 gcalcli）？
- **安裝 checklist**：
  - [ ] 取得 OAuth 憑證（可能跟 Gmail 共用）
  - [ ] 依 AI 查到的最新步驟安裝
  - [ ] 跑驗證：「今天的行程有哪些？」
  - [ ] 回來打勾 + 在「備註」欄記下任何踩坑
- **備註**：（執行完畢後寫這裡）

### 🟡 Firecrawl — 尚未整合

- **用途**：抓網頁內容、整理文章重點、搜尋資料
- **建議路線**：MCP（Firecrawl MCP 是目前抓網頁最順的方案）
- **執行時要查的事情**：
  - [ ] Firecrawl MCP 官方最新安裝方式？
  - [ ] 免費額度多少？夠用嗎？
  - [ ] 有沒有替代方案？（Claude Code 內建 WebFetch 也能抓，但功能較少）
- **安裝 checklist**：
  - [ ] 到 Firecrawl 官網註冊取得 API key
  - [ ] 依 AI 查到的最新步驟安裝
  - [ ] 跑驗證：「幫我抓這個網頁的內容：[一個網址]」
  - [ ] 回來打勾 + 在「備註」欄記下任何踩坑
- **備註**：（執行完畢後寫這裡）

### 🟡 LINE — 觀察中

- **用途**：台灣最常用的通訊軟體
- **建議路線**：目前沒有成熟的 AI agent 整合方案
- **執行時要查的事情**：
  - [ ] LINE 有沒有出官方 API/MCP？（搜尋 `LINE bot Claude Code integration 2026`）
  - [ ] 有沒有社群做的替代方案？
  - [ ] 是否可以用 LINE Notify API 做單向通知？
- **安裝 checklist**：
  - [ ] 等到有可行方案再執行
- **備註**：目前建議用「複製 LINE 訊息貼給 AI」的方式替代

---

## 進度總覽

- 🟢 已整合：1 個（GitHub）
- 🟡 尚未整合：3 個（Gmail、Google Calendar、Firecrawl）
- ⏳ 觀察中：1 個（LINE）

**下次執行建議**：從 Gmail 或 Google Calendar 先開始（可以共用 OAuth），一次一個，不要貪多。

---

## 給未來 AI 執行時的指引（不要刪這段）

當用戶打開這份文件跟你說「幫我挑 [某個工具] 來裝」時，請按以下步驟：

### 1. 確認範圍

用 `AskUserQuestion` 確認：
- 你要整合 [工具名]，對嗎？
- 整合的主要用途是什麼？（從計畫文件的「用途」欄讀出來讓他確認）

### 2. 用網路搜尋查最新整合方式

**這一步絕對不要跳過，也不要用你訓練資料裡的舊資訊。** 執行：

1. 用 WebSearch / WebFetch 或 MCP 的搜尋工具查以下問題：
   - `"[工具名]" Claude Code MCP integration 2026`
   - `"[工具名]" official CLI tool`
   - `"[工具名]" REST API authentication`
2. 優先看官方文件、GitHub README、官方 blog 公告
3. 對照計畫文件的「建議路線」，看看有沒有更新/更好的方案
4. **把你查到的結果整理成一段話告訴用戶**：「我查到 [工具名] 目前最推薦的整合方式是 [XX]，因為 [原因]。要不要照這個走？」
5. 用 `AskUserQuestion` 讓用戶拍板

### 3. 執行安裝

根據拍板的路線：

- **CLI 路線**：幫用戶安裝該 CLI 工具（brew / npm / pip，依你查到的官方推薦），引導完成 auth，跑一個驗證指令
- **API 路線**：
  - 引導用戶取得 API key / token（告訴他官方取得頁面的網址）
  - 存到 `.env`，key 命名用大寫 + 底線（例如 `NOTION_TOKEN`）
  - 在 `000_Agent/skills/` 底下建一個該服務的 skill
- **MCP 路線**：
  - 編輯 `~/.claude.json` 的 `mcpServers` 區段加入新的 entry
  - 完成 auth（OAuth 跳瀏覽器、或貼 token）
  - 重新載入 MCP

### 4. 驗證

用一個實際指令測試這個整合真的能用。

### 5. 更新計畫文件

用 `Edit` 工具更新這份計畫：
- 該工具區塊的標題從 🟡 改成 🟢
- 安裝 checklist 全部打勾
- 備註欄寫：「實際用了 [路線]、裝的套件版本 [版本號]、踩坑 [...]、驗證指令 [...]」
- 進度總覽數字調整

### 6. 告訴用戶下一步

「[工具名] 整合完成！剩下 [N] 個工具。建議一週後再挑下一個來裝，讓這個先用熟。」
