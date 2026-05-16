# Fallback Design Rules — Claude 自生模式的三條鐵律

UUPM 未安裝或失敗時，Claude 用自己的美感生成。沒有產業資料庫、沒有 anti-pattern 清單，但遵守以下三條鐵律不會難看。

---

## 鐵律 1：字體只配一組

**只允許這幾種組合之一，不要自由發揮：**

| 組合 | Headline | Body | 適合 |
|:--|:--|:--|:--|
| A. 襯線 + 無襯線 | Noto Serif TC | Noto Sans TC | 編輯感、沉穩、高客單 |
| B. 純無襯線（中） | Noto Sans TC 700 | Noto Sans TC 400 | 現代、SaaS、簡潔 |
| C. 雙無襯線 | Space Grotesk | Inter | 英文為主、科技感 |

**不允許：** 手寫體、裝飾字體、多於兩種字體混用。

選哪組根據 A3（調性關鍵字）：
- 「沉穩／專業／高級」→ A
- 「現代／清晰／SaaS」→ B
- 「科技／極簡／英文」→ C

### Google Fonts import 範本

```html
<!-- 組合 A -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@400;500;700&display=swap" rel="stylesheet">

<!-- 組合 B -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">

<!-- 組合 C -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
```

---

## 鐵律 2：主色 + CTA 色 + 中性色三種內

**只允許 3 個主要顏色：**

```css
:root {
  --color-primary: /* 品牌主色 */;
  --color-cta: /* 按鈕／倒數／急迫元素 */;
  --color-text: /* 文字與中性色 */;

  /* 衍生色（從上面算出） */
  --color-bg: /* 背景，通常是主色的極淺色或白色 */;
  --color-muted: /* 次要文字，text 的 opacity 0.6 */;
  --color-border: /* 分隔線，text 的 opacity 0.1 */;
}
```

### 建議調色盤（依調性）

| 調性 | Primary | CTA | Text | Bg |
|:--|:--|:--|:--|:--|
| 沉穩專業 | `#1E3A5F`（深藍） | `#D4A017`（金） | `#1A1A1A` | `#FAFAF8` |
| 活力年輕 | `#FF5A5F`（珊瑚） | `#2B2D42`（炭） | `#1A1A1A` | `#FFFFFF` |
| 科技現代 | `#0F172A`（深炭） | `#3B82F6`（藍） | `#0F172A` | `#F8FAFC` |
| 高級編輯 | `#2D2A32`（黑紫） | `#C9A87C`（駝） | `#2D2A32` | `#FAF7F2` |
| 自然有機 | `#4A5D3A`（苔綠） | `#E07856`（陶） | `#2D2A32` | `#F5F2E8` |

根據 A3 調性關鍵字挑一組，或從這幾組衍生微調。

**禁止：**
- 超過 3 個主色（3 + 衍生色不算）
- 高飽和彩虹漸層（AI purple/pink gradient）
- 對比度低於 4.5:1

---

## 鐵律 3：間距走 8px base grid

**所有間距用 8 的倍數：**

| Token | px | Tailwind | 用途 |
|:--|:--|:--|:--|
| `space-1` | 4px | `p-1` | 微距（icon 旁） |
| `space-2` | 8px | `p-2` | 緊密 |
| `space-3` | 12px | `p-3` | 標準小 |
| `space-4` | 16px | `p-4` | 標準 |
| `space-6` | 24px | `p-6` | 區塊內 |
| `space-8` | 32px | `p-8` | 卡片 padding |
| `space-12` | 48px | `p-12` | section 間 |
| `space-16` | 64px | `p-16` | 大分隔 |
| `space-24` | 96px | `py-24` | section 垂直間距（桌機） |

### Section 垂直節奏

桌機：section 間 `py-24`（96px）
手機：section 間 `py-16`（64px）

Hero 區更大：桌機 `py-32`（128px），手機 `py-20`（80px）。

### Container 寬度

內容最大寬度：`max-w-2xl`（672px），閱讀型
宣傳／視覺：`max-w-4xl`（896px）
Grid／多欄：`max-w-5xl`（1024px）

**不允許：** 任意奇數間距（13px、17px、25px 之類）。

---

## 組合成 Tailwind 配置

生成 HTML 時把上面的規則注入成 inline `<style>` 或 Tailwind config：

```html
<script src="https://cdn.tailwindcss.com"></script>
<script>
  tailwind.config = {
    theme: {
      extend: {
        colors: {
          primary: 'var(--color-primary)',
          cta: 'var(--color-cta)',
        },
        fontFamily: {
          headline: ['var(--font-headline)'],
          body: ['var(--font-body)'],
        },
      },
    },
  };
</script>
```

---

## 最終檢查（每次 fallback 生成後跑）

- [ ] 字體用了剛好兩種（或一種）
- [ ] 主色 + CTA + 中性色，共 3 個主色
- [ ] 所有 padding / margin 都是 8 的倍數
- [ ] 對比度 4.5:1 以上
- [ ] `prefers-reduced-motion` 尊重
- [ ] CTA 按鈕有 `cursor-pointer` + hover transition 200-300ms
- [ ] 響應式斷點：375 / 768 / 1024

任何一項不符合，在 Step 5 的輸出訊息裡附 ⚠️ 提醒。