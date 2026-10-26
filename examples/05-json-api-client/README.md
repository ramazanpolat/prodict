# 05 - JSON API client

The complete round trip a typical API client does. `blog.json` stands in for a REST
response: a user with posts, each post with comments, some numbers sent as strings and
one field `null`.

What it shows:

1. **Read:** `User.from_dict(json.loads(...))` builds `User`, `Post` and `Comment`
   instances with converted types in one call.
2. **Compute:** methods on the models (`total_likes()`, `commenters()`).
3. **Change:** append new models, add keys that are not in the schema.
4. **Write:** `json.dumps(user)` works because a Prodict is a dict; `to_dict(exclude_none=True)`
   drops `None` values.
5. **Copy:** `copy.deepcopy` and `pickle` keep the model classes.

See [the serialization guide](../../docs/guides/serialization.md) for every `to_dict()` option.

```bash
uv run python examples/05-json-api-client/main.py
```

```
rambo 1
['Hello World', 'Leave the old behind']
42
['posts', 'user_id', 'user_name']
05-json-api-client: ok
```
