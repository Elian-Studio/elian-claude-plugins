# 하우스 컴포넌트 카탈로그

문서를 "디자인된 것"처럼 보이게 하는 리치 컴포넌트 모음. **Markdown 안에 raw HTML 블록으로 그대로 붙여넣으면**
`build_doc.py` 가 통과시키고, 하우스 CSS가 자동으로 스타일을 입힌다.

**철칙**: 인라인 `style=` 이나 새 CSS를 만들지 말 것. 아래 클래스만 조합한다. 그래야 모든 문서 톤이 통일된다.
색이 정말 필요하면 변수(`var(--accent)`, `var(--tip)`, `var(--warn)`, `var(--danger)`, `var(--muted)`)만 재사용.

---

## 콜아웃 (Markdown 문법 권장)

대부분 raw HTML 없이 GitHub식 문법으로 충분하다:

```markdown
> [!NOTE]
> 일반 참고. 맥락이나 배경 설명.

> [!TIP]
> 권장 사항이나 요령.

> [!IMPORTANT]
> 놓치면 안 되는 핵심.

> [!WARNING]
> 주의해야 할 위험 요소.

> [!CAUTION]
> 하면 안 되는 것 / 파괴적 동작 경고.

> [!INFO]
> 부가 정보(중립 톤).
```

여러 줄·목록도 콜아웃 안에 넣을 수 있다(각 줄 앞에 `>`).

---

## 카드

단일 카드 — 하나의 묶음을 박스로:

```html
<div class="card">
  <div class="card-title">아키텍처 결정</div>
  커넥션 풀을 HikariCP로 통일하고 최대 풀 크기를 50으로 상향한다.
</div>
```

카드 그리드 — 병렬 항목 2~4개를 나란히 (auto-fit, 좁아지면 자동 한 줄씩):

```html
<div class="card-grid">
  <div class="card"><div class="card-title">백엔드</div>Spring Boot 3.x</div>
  <div class="card"><div class="card-title">프론트</div>Vue 3 + Pinia</div>
  <div class="card"><div class="card-title">DB</div>PostgreSQL 16</div>
</div>
```

---

## KPI 타일

숫자 지표를 강조. `delta up`(초록)·`delta down`(빨강)으로 증감 표시:

```html
<div class="kpi-grid">
  <div class="kpi">
    <div class="num">820ms</div>
    <div class="label">p95 응답시간</div>
    <div class="delta down">+210ms</div>
  </div>
  <div class="kpi">
    <div class="num">99.2%</div>
    <div class="label">가용성</div>
    <div class="delta up">+0.3%p</div>
  </div>
</div>
```

`delta` 줄은 변화량이 실제로 있을 때만. 단순 현황이면 생략.

---

## 2단 비교 (Before / After, 안 / 밖, 장 / 단)

```html
<div class="cols2">
  <div class="card"><div class="card-title">AS-IS</div>동기 호출, 평균 820ms</div>
  <div class="card"><div class="card-title">TO-BE</div>비동기 + 캐시, 평균 90ms</div>
</div>
```

---

## 단계 리스트 (절차 / 워크플로우)

번호가 매겨진 시각적 스텝. 가이드·튜토리얼·절차 설명에 적합:

```html
<div class="steps">
  <div class="step">
    <div class="n">1</div>
    <div class="st-body"><b>의존성 설치</b><br>프로젝트 루트에서 <code>./gradlew build</code> 실행.</div>
  </div>
  <div class="step">
    <div class="n">2</div>
    <div class="st-body"><b>환경 변수 설정</b><br><code>.env</code> 에 DB 접속 정보를 채운다.</div>
  </div>
</div>
```

> 단순 순서 목록이면 Markdown 의 `1. 2. 3.` 으로 충분하다. `.steps` 는 각 단계에 설명이 붙는
> "절차 안내"일 때 쓴다.

---

## 배지 / 태그

상태·라벨을 인라인으로:

```html
<span class="badge badge-accent">진행중</span>
<span class="badge badge-tip">완료</span>
<span class="badge badge-warn">검토필요</span>
<span class="badge badge-danger">차단</span>
<span class="badge badge-muted">보류</span>
```

표 셀이나 제목 옆에 인라인으로 섞어 쓸 수 있다.

---

## 데이터 표

표는 Markdown 으로 쓰면 자동으로 스타일이 입혀진다(별도 클래스 불필요):

```markdown
| 항목 | 이전 | 이후 | 변화 |
|------|----:|----:|:----:|
| p95 응답 | 820ms | 90ms | <span class="badge badge-tip">−89%</span> |
| 오류율 | 3.4% | 0.8% | <span class="badge badge-tip">개선</span> |
```

- 정렬: `:---` 좌, `---:` 우, `:---:` 중앙.
- 셀 안 줄바꿈은 `<br>`, 인라인 코드는 백틱.

---

## 코드 블록

언어를 명시하면 상단에 작은 라벨이 붙는다:

````markdown
```java
public record PaymentResult(String id, long amountKrw) {}
```
````

---

## 접이식 (긴 부록 / 원본 데이터)

raw HTML `<details>` 를 그대로 쓴다:

```html
<details>
  <summary>전체 로그 (클릭하여 펼치기)</summary>

  ```
  2026-06-07 12:00:01 WARN  pool exhausted
  ```
</details>
```

---

## 이미지 / 그림

```markdown
![결제 플로우 다이어그램](./images/payment-flow.png)
```

캡션이 필요하면 raw HTML `figure`:

```html
<figure>
  <img src="./images/payment-flow.png" alt="결제 플로우">
  <figcaption>그림 1. 결제 요청 처리 플로우</figcaption>
</figure>
```

이미지는 출력 HTML 옆 `images/` 에 두고 상대 경로로 참조한다(자기완결 HTML은 텍스트만 인라인되고
이미지는 외부 파일이다 — 공유 시 함께 전달).
