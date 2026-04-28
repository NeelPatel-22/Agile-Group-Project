# Database Diagram

Use this as the database reference when integrating login, signup, recipes, likes, saves, and comments.

```mermaid
erDiagram
    USER {
        int id PK
        string username UK
        string email UK
        string password_hash
        string bio
        string profile_image
        datetime created_at
    }

    RECIPE {
        int id PK
        string title
        string category
        string cook_time
        string servings
        text description
        text why_people_love_it
        string flavor_notes
        string skill_level
        string best_for
        string pair_with
        string spice_level
        text dietary_cautions
        text ingredients
        text steps
        string image_url
        boolean comments_hidden
        datetime created_at
        int user_id FK
    }

    COMMENT {
        int id PK
        text content
        boolean is_hidden
        datetime created_at
        int user_id FK
        int recipe_id FK
        int parent_id FK
    }

    LIKE {
        int id PK
        int user_id FK
        int recipe_id FK
        datetime created_at
    }

    SAVED_RECIPE {
        int id PK
        int user_id FK
        int recipe_id FK
        datetime created_at
    }

    USER ||--o{ RECIPE : creates
    USER ||--o{ COMMENT : writes
    USER ||--o{ LIKE : likes
    USER ||--o{ SAVED_RECIPE : saves

    RECIPE ||--o{ COMMENT : has
    RECIPE ||--o{ LIKE : receives
    RECIPE ||--o{ SAVED_RECIPE : saved_as

    COMMENT ||--o{ COMMENT : replies
```

## Important Constraints

- `user.username` must be unique.
- `user.email` must be unique.
- `like.user_id + like.recipe_id` must be unique.
- `saved_recipe.user_id + saved_recipe.recipe_id` must be unique.
- `recipe.user_id` connects each recipe to its creator.
- `comment.parent_id` is nullable and is used for replies.
