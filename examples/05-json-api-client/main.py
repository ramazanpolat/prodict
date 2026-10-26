"""A complete round trip: JSON in, typed models in the middle, JSON out.

blog.json stands in for a REST response. Its numbers arrive partly as strings and
one field is null, the way real APIs often send them.
"""
import copy
import json
import pickle
from pathlib import Path
from typing import List

from prodict import Prodict


class Comment(Prodict):
    user_id: int
    comment: str
    date: str


class Post(Prodict):
    title: str
    text: str
    date: str
    likes: int
    comments: List[Comment]

    def commenters(self):
        return {comment.user_id for comment in self.comments}


class User(Prodict):
    user_id: int
    user_name: str
    email: str
    posts: List[Post]

    def total_likes(self):
        return sum(post.likes for post in self.posts)


def load_user(path: Path) -> User:
    return User.from_dict(json.loads(path.read_text()))


user = load_user(Path(__file__).with_name('blog.json'))

# 1. Read: typed, nested, and completed by the IDE.
print(user.user_name, user.user_id)  # rambo 1
print([post.title for post in user.posts])  # ['Hello World', 'Leave the old behind']
assert user.user_id == 1
assert isinstance(user.posts[0], Post)
assert isinstance(user.posts[0].comments[0], Comment)
assert user.posts[0].comments[0].user_id == 2  # "2" in the JSON

# 2. Compute with model methods.
print(user.total_likes())  # 42
assert user.total_likes() == 42
assert user.posts[0].commenters() == {2, 3}

# 3. Change it: new posts are built as models, extra keys are allowed.
user.posts.append(Post(title='Draft', text='...', date='2018-03-01 00:00:00', likes='0', comments=[]))
user.posts[-1].draft = True
assert user.total_likes() == 42

# 4. Write it back out. Prodict is a dict, so json.dumps takes it directly.
payload = json.dumps(user)
assert json.loads(payload)['posts'][2]['draft'] is True

# to_dict() controls the shape: drop None values at the top level here.
clean = user.to_dict(exclude_none=True)
print(sorted(clean))  # ['posts', 'user_id', 'user_name']
assert 'email' not in clean

# 5. Copies and pickling keep the model types.
clone = copy.deepcopy(user)
assert isinstance(clone, User) and clone == user and clone is not user
restored = pickle.loads(pickle.dumps(user))
assert isinstance(restored, User) and restored == user

print('05-json-api-client: ok')
