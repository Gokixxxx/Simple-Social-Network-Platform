# README.md

模拟社交网络数据库。

确保已安装 Python 3.10+，然后安装项目依赖：`pip install mysql-connector-python python-dotenv`。

在项目根目录（即本 `README.md` 所在目录）创建 `.env` 文件 ：

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456789
DB_NAME=social_network
```

并将对应的值（端口、用户名、密码）改为本地 SQL server 的数据。

确保本地 MySQL 中已存在名为 `social_network` 的数据库。可以通过`mysql -u root -p`启动 MySQL 客户端，然后执行`SHOW DATABASES;`命令检查本地数据库。如不存在`social_network`，则需要先在客户端中创建，执行命令` CREATE DATABASE social_network CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; `。如果想要删除数据库，可以使用命令`DROP DATABASE social_network;`。

使用时进入`/project`，先运行一次`create_tables.py`建表，然后运行`set_admin.py`初始化管理员，最后运行命令行前端`main.py`。

![ER](./ER.png)

