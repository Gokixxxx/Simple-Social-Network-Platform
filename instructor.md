## 任务说明

### 框架

```python
project/
├── main.py                          # 前端
├── backend/
│   ├── __init__.py                  # 空文件，标记为包
│   ├── db_connection.py             # 数据库连接
│   ├── user_manager.py              # 用户管理
│   ├── moment_manager.py            # 朋友圈管理
│   └── admin_manager.py             # 管理员管理
└── init_db.py                       # 数据库初始化（测试）
```



### 表设计

需要设计E-R图。

需要根据E-R图导出表设计，一个可能的表设计方式是：（之后根据E-R图再改）

1. users

| 字段名       | 数据类型                | 约束                        | 说明                                          |
| ------------ | ----------------------- | --------------------------- | --------------------------------------------- |
| `user_id`    | INT                     | PRIMARY KEY, AUTO_INCREMENT | 用户唯一ID                                    |
| `username`   | VARCHAR(50)             | UNIQUE, NOT NULL            | 用户名 (用于登录)                             |
| `password`   | VARCHAR(255)            | NOT NULL                    | 密码 (实际应用中应加密存储)                   |
| `name`       | VARCHAR(50)             |                             | 姓名                                          |
| `gender`     | ENUM('M', 'F', 'Other') |                             | 性别                                          |
| `birth_date` | DATE                    |                             | 出生日期                                      |
| `age`        | INT                     |                             | 年龄 (可由`birth_date`计算得出，也可单独存储) |

2. admins

| 字段名           | 数据类型                | 约束                        | 说明                    |
| ---------------- | ----------------------- | --------------------------- | ----------------------- |
| `admin_id`       | INT                     | PRIMARY KEY, AUTO_INCREMENT | 管理员唯一ID            |
| `admin_username` | VARCHAR(50)             | UNIQUE, NOT NULL            | 管理员用户名 (用于登录) |
| `password`       | VARCHAR(255)            | NOT NULL                    | 密码                    |
| `name`           | VARCHAR(50)             |                             | 姓名                    |
| `gender`         | ENUM('M', 'F', 'Other') |                             | 性别                    |
| `birth_date`     | DATE                    |                             | 出生日期                |
| `age`            | INT                     |                             | 年龄                    |

3. friendships

| 字段名                 | 数据类型    | 约束                                                    | 说明                   |
| ---------------------- | ----------- | ------------------------------------------------------- | ---------------------- |
| `user_id`              | INT         | FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`)   | 用户A的ID              |
| `friend_id`            | INT         | FOREIGN KEY (`friend_id`) REFERENCES `users`(`user_id`) | 用户B的ID              |
| `group_name`           | VARCHAR(50) | DEFAULT '默认分组'                                      | 好友分组名称           |
| `(user_id, friend_id)` | -           | PRIMARY KEY                                             | 联合主键，防止重复添加 |

4. moments

| 字段名             | 数据类型     | 约束                                                         | 说明                           |
| ------------------ | ------------ | ------------------------------------------------------------ | ------------------------------ |
| `moment_id`        | INT          | PRIMARY KEY, AUTO_INCREMENT                                  | 朋友圈唯一ID                   |
| `user_id`          | INT          | FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE | 发布者ID                       |
| `content`          | VARCHAR(500) | NOT NULL                                                     | 朋友圈内容 (假设字数限制为500) |
| `last_update_time` | DATETIME     | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP        | 最后更新时间                   |

5. comments

| 字段名         | 数据类型     | 约束                                                        | 说明             |
| -------------- | ------------ | ----------------------------------------------------------- | ---------------- |
| `comment_id`   | INT          | PRIMARY KEY, AUTO_INCREMENT                                 | 评论唯一ID       |
| `moment_id`    | INT          | FOREIGN KEY (`moment_id`) REFERENCES `moments`(`moment_id`) | 被评论的朋友圈ID |
| `user_id`      | INT          | FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`)       | 评论者ID         |
| `content`      | VARCHAR(255) | NOT NULL                                                    | 评论内容         |
| `comment_time` | DATETIME     | DEFAULT CURRENT_TIMESTAMP                                   | 评论时间         |

触发器：

1. 朋友圈被删除时，其对应的评论也应该被删除。
2. 用户被注销时，其对应的朋友圈和评论也应该被删除。（该条可能可以通过外键实现）

内置函数：

python与数据库的连接代码：`create_connection`创建连接，`close_connection`关闭连接，`execute_query`执行SELECT操作，`execute_update`执行增删改操作。

`manager`只应调用两个`execute`函数，而与`connection`操作解耦。注意调用时为了防止注入攻击，参数需要先用`%s`占位，之后再附上一个tuple依次给参数传值。举个例子：查是否存在某个`user_id`的用户时，应写为`execute_query("SELECT user_id FROM users WHERE username = %s", ('Monkey',))`，而不能写为`execute_query("SELECT user_id FROM users WHERE username = 'Monkey'")`，后者有注入风险。



### 前端

1. 用户端

   ```python
   # 用户注册
   register_user(username: str, password: str) -> dict
   # 返回: {"success": True/False, "message": "注册成功/失败原因", "user_id": int}
   
   # 用户登录
   login_user(username: str, password: str) -> dict
   # 返回: {"success": True/False, "message": "登录成功/失败原因", "user_id": int, "name": str}
   
   # 获取用户个人信息
   get_user_profile(user_id: int) -> dict
   # 返回: {"user_id": int, "username": str, "name": str, "gender": str, "birth_date": str, "age": int}
   
   # 更新用户个人信息
   update_user_profile(user_id: int, name: str=None, gender: str=None, birth_date: str=None) -> dict
   # 返回: {"success": True/False, "message": "更新成功/失败原因"}
   ```

2. 好友管理

   ```python
   # 搜索用户（通过用户名）
   search_users(keyword: str) -> list
   # 返回: [{"user_id": int, "username": str, "name": str}, ...]
   
   # 添加好友
   add_friend(user_id: int, friend_id: int, group_name: str="默认分组") -> dict
   # 返回: {"success": True/False, "message": "添加成功/失败原因"}
   
   # 删除好友
   remove_friend(user_id: int, friend_id: int) -> dict
   # 返回: {"success": True/False, "message": "删除成功/失败原因"}
   
   # 获取好友列表（可按分组筛选）
   get_friends_list(user_id: int, group_name: str=None) -> list
   # 返回: [{"friend_id": int, "username": str, "name": str, "group_name": str}, ...]
   
   # 修改好友分组
   update_friend_group(user_id: int, friend_id: int, new_group_name: str) -> dict
   # 返回: {"success": True/False, "message": "修改成功/失败原因"}
   ```

3. 朋友圈

   ```python
   # 发表朋友圈
   post_moment(user_id: int, content: str) -> dict
   # 返回: {"success": True/False, "message": "发布成功/失败原因", "moment_id": int}
   
   # 修改朋友圈
   update_moment(moment_id: int, user_id: int, new_content: str) -> dict
   # 返回: {"success": True/False, "message": "修改成功/失败原因"}
   
   # 删除朋友圈（会触发删除相关评论）
   delete_moment(moment_id: int, user_id: int) -> dict
   # 返回: {"success": True/False, "message": "删除成功/失败原因"}
   
   # 查看自己的朋友圈
   get_my_moments(user_id: int) -> list
   # 返回: [{"moment_id": int, "content": str, "last_update_time": str, "comment_count": int}, ...]
   
   # 查看好友的朋友圈（包含评论）
   get_friends_moments(user_id: int) -> list
   # 返回: [
   #   {
   #     "moment_id": int,
   #     "user_id": int,
   #     "username": str,
   #     "content": str,
   #     "last_update_time": str,
   #     "comments": [
   #       {"comment_id": int, "commenter_id": int, "commenter_name": str, "content": str, "comment_time": str},
   #       ...(other comments)
   #     ]
   #   },
   #   ...(other moments)
   # ]
   
   # 评论朋友圈
   add_comment(moment_id: int, user_id: int, content: str) -> dict
   # 返回: {"success": True/False, "message": "评论成功/失败原因", "comment_id": int}
   
   # 删除评论（只能删除自己的评论）
   delete_comment(comment_id: int, user_id: int) -> dict
   # 返回: {"success": True/False, "message": "删除成功/失败原因"}
   ```

4. 管理员个人信息

   ```python
   # 管理员登录
   login_admin(admin_username: str, password: str) -> dict
   # 返回: {"success": True/False, "message": "登录成功/失败原因", "admin_id": int, "name": str}
   
   # 获取管理员个人信息
   get_admin_profile(admin_id: int) -> dict
   # 返回: {"admin_id": int, "admin_username": str, "name": str, "gender": str, "birth_date": str, "age": int}
   
   # 更新管理员个人信息
   update_admin_profile(admin_id: int, name: str=None, gender: str=None, birth_date: str=None) -> dict
   # 返回: {"success": True/False, "message": "更新成功/失败原因"}
   ```

5. 用户管理

   ```python
   # 浏览所有用户列表（不包含敏感信息）
   get_all_users() -> list
   # 返回: [{"user_id": int, "username": str}, ...]
   
   # 注销用户（删除用户及其所有相关数据）
   delete_user_by_admin(admin_id: int, target_user_id: int) -> dict
   # 返回: {"success": True/False, "message": "注销成功/失败原因"}
   ```

6. 朋友圈管理

   ```python
   # 浏览所有朋友圈（用于审核）
   get_all_moments_for_review() -> list
   # 返回: [
   #   {
   #     "moment_id": int,
   #     "user_id": int,
   #     "username": str,
   #     "content": str,
   #     "last_update_time": str,
   #     "comments": [...]
   #   },
   #   ...
   # ]
   
   # 删除违规朋友圈（管理员权限）
   delete_moment_by_admin(admin_id: int, moment_id: int) -> dict
   # 返回: {"success": True/False, "message": "删除成功/失败原因"}
   ```