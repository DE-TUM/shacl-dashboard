Corrected version using `frontend/src/components` as the root:

---

# How to Add a New Page to the SHACL Dashboard (Vue 3 + Flask)

This guide explains how to extend the SHACL Dashboard with a new frontend page and corresponding backend API support.

---

## 1. Create a Vue Component

Create a new file:

```
frontend/src/components/Views/MyNewPage.vue
```

Example content:

```vue
<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">My New Page</h1>
    <p>Content coming soon...</p>
  </div>
</template>

<script setup>
// logic goes here
</script>
```

---

## 2. Register the Route

Edit `frontend/src/router/index.js`:

```js
import MyNewPage from "@/components/Views/MyNewPage.vue";

const routes = [
  // ...existing routes
  { path: "/my-new-page", name: "MyNewPage", component: MyNewPage },
];
```

---

## 3. Add to Navigation Sidebar

In `frontend/src/components/Layout/Navigation.vue`, add a list item:

```vue
<v-list-item>
  <router-link :to="'/my-new-page'" @click.native="buttonClicked('My New Page')">
    <v-btn text class="button-text-wrap blue-btn">My New Page</v-btn>
  </router-link>
</v-list-item>
```

---

## 4. Add a Flask Blueprint Route

In `backend/routes/my_new_page_routes.py`:

```python
from flask import Blueprint, jsonify, request

my_new_page_bp = Blueprint("my_new_page", __name__)

@my_new_page_bp.route("/my-new-endpoint", methods=["GET"])
def example():
    param = request.args.get("param", default="default_value")
    return jsonify({"message": f"You sent: {param}"})
```

Register it in `backend/routes/__init__.py`:

```python
from .my_new_page_routes import my_new_page_bp

blueprints = [
    shapes_overview_bp,
    landing_bp,
    homepage_bp,
    shape_view_bp,
    my_new_page_bp,
]
```

---

## 5. Add Backend Logic (Optional)

Create `backend/functions/my_new_page_service.py`:

```python
def compute_new_statistic(param):
    return {"result": f"Processed {param}"}
```

Import in `backend/functions/__init__.py`:

```python
from .my_new_page_service import (
    compute_new_statistic,
)
```

Add to `__all__`:

```python
__all__ = [
    # existing entries ...
    "compute_new_statistic",
]
```

---

## 6. Connect Frontend to API

In `frontend/src/components/Views/MyNewPage.vue`:

```js
import { ref, onMounted } from "vue";
import axios from "axios";

const result = ref("");

onMounted(async () => {
  try {
    const response = await axios.get("/my-new-endpoint", {
      params: { param: "hello" },
    });
    result.value = response.data.result || response.data.message;
  } catch (error) {
    result.value = "Error contacting backend";
  }
});
```

In the template:

```vue
<p>API Response: {{ result }}</p>
```

---

## Summary

| Task                   | Location                                      | Action                           |
| ---------------------- | --------------------------------------------- | -------------------------------- |
| Frontend component     | `frontend/src/components/Views/MyNewPage.vue` | Create Vue page                  |
| Router entry           | `frontend/src/router/index.js`                | Add route                        |
| Navigation link        | `frontend/src/components/Navigation.vue`      | Add `<router-link>`              |
| Flask blueprint        | `backend/routes/my_new_page_routes.py`        | Create route                     |
| Blueprint registration | `backend/routes/__init__.py`                  | Import and register blueprint    |
| Backend logic          | `backend/functions/my_new_page_service.py`    | Implement function               |
| Functions registration | `backend/functions/__init__.py`               | Import and add to `__all__` list |
| API call from frontend | `frontend/src/components/Views/MyNewPage.vue` | Use axios to fetch data          |
