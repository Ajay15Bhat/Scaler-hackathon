---
Title: Warehouse Agent
Emoji: 🚀
ColorFrom: blue
ColorTo: green
sdk: docker
app_file: app.py
pinned: false
---
# Hybrid Warehouse Agent (OpenEnv)

## 📌 Overview
This project simulates a real-world warehouse order fulfillment system where an autonomous agent collects items and delivers them to a drop zone.

The agent must:
- Navigate a grid warehouse
- Pick correct items
- Optimize delivery routes
- Manage time and battery constraints

---

## 🎯 Motivation
Warehouse automation is a real-world logistics problem. This environment models:
- Order batching
- Path optimization
- Resource constraints

---

## 🧠 Environment Details

### Grid Layout
- S → Start
- A, B, C → Items
- D → Drop zone
- X → Obstacles

---

## 📥 Observation Space

```python
{
  "agent_position": [row, col],
  "inventory": [items],
  "current_order": [items] or None,
  "orders_completed": int,
  "time": int,
  "battery": int
}
