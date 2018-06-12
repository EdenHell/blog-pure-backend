# blog-pure-backend

[![python3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org)
[![Flask1.0.2](https://img.shields.io/badge/flask-1.0.2-green.svg)](http://flask.pocoo.org)

一个基于 flask 的纯博客后端程序，没有任何前端代码，仅作为一个 GraphQL Server 提供 API。

此后端程序可以跟任意使用 GraphQL 查询语言的 `SPA` 前端博客程序进行组合，

只要其支持下面所谓的 `SGSFB`，全称是 ` Standard GraphQL Schema For Blogs` （笑）

## SGSFB

```graphql
schema {
    query: Query
    mutation: Mutation
}

type Query {
    posts(postFilter: PostFilter!): [Post!]!
    tags(postId: Int): [String!]!
    about: About
    adminAuth(password: String!): AuthResult!
}

type Mutation {
    createPost(password: String! title: String! body: String!): CreatePost
    updatePost(password: String! postId: String! title: String body: String): UpdatePost
}

scalar YearTime

enum AuthResult {
    SUCCESS
    FAILURE
}

input PostFilter {
    offset: Int!
    limit: Int!
    tag: String
    yearTime: YearTime
}

type Post {
    postId: String
    title: String
    body: String
    createTime: DateTime
    updateTime: DateTime
}

type About {
    name: String
    age: Int
    sex: String
    github: String
    mail: String
}

type CreatePost {
    postId: String
}

type UpdatePost {
    ok: Boolean
    message: String
}
```
