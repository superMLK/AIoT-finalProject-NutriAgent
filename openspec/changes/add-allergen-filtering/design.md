# OpenSpec Technical Design: Food Allergen Input & Pruning
Change ID: `add-allergen-filtering`

## 1. Data Models & Schemas

### 1.1 User Profile Allergen Field
In `data/sample_health_reports.json`:
```json
{
  "profile_id": "P_001_HYPERTENSION",
  "allergens": ["seafood", "peanuts"]
}
```

### 1.2 Food Catalog Allergen Field
In `data/meal_catalog.json`:
```json
{
  "meal_id": "FIT_002",
  "dish_name": "清蒸鮮嫩鯛魚紫米餐盒",
  "allergens": ["seafood", "fish"]
}
```

---

## 2. Allergen Categorization & Alias Mapping
To prevent false-negative escapes (e.g. user selects `seafood` but meal is labeled `fish`), `ClinicalRulesEngine` maps macro categories to sub-ingredient tags:

| 標準過敏原類別 | 包含關鍵字 / 別名 (Aliases) |
| :--- | :--- |
| `seafood` (海鮮) | `seafood`, `fish`, `shellfish`, `shrimp`, `crab`, `squid`, `clam` |
| `peanuts` (花生堅果) | `peanuts`, `peanut`, `nuts`, `tree_nuts`, `almond`, `walnut` |
| `gluten` (麩質小麥) | `gluten`, `wheat`, `barley`, `rye` |
| `dairy` (奶製品乳糖) | `dairy`, `milk`, `cheese`, `butter` |
| `egg` (蛋類) | `egg`, `eggs` |
| `soy` (大豆黃豆) | `soy`, `soybean`, `tofu` |
| `sesame` (芝麻) | `sesame` |

---

## 3. Pruning Algorithm
In `src/clinical_rules.py`:
```python
def check_allergens(meal_allergens: List[str], user_allergens: List[str]) -> Tuple[bool, str]:
    for u_all in user_allergens:
        aliases = ALLERGEN_ALIAS_MAP.get(u_all.lower(), {u_all.lower()})
        for m_all in meal_allergens:
            if m_all.lower() in aliases:
                return True, f"餐點含有過敏食材 [{u_all}]"
    return False, ""
```
If `check_allergens` returns `True`, the meal is strictly disqualified from the Safe Candidate Pool.

---

## 4. UI Design
In `app.py`:
A dedicated "⚠️ 食物過敏原 (Food Allergens)" multi-select checkbox group is placed in the left panel. Users can toggle allergens on the fly, and the `/api/recommend` endpoint dynamically ingests `allergens: [...]`.
