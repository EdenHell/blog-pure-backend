# blog-pure-backend
一个基于 flask 的纯博客后端程序，没有任何前端代码，仅作为一个 GraphQL Server 提供 API。

此后端程序可以跟任意使用 GraphQL 查询语言的 `SPA` 前端博客程序进行组合，

只要其支持下面所谓的 `SGSFB`，全称是 ` Standard GraphQL Schema For Blogs` （笑）

## SGSFB

```graphql
type Query {
  essay(id: ID!): String
  authorName: String
  authorAge: String
  authorSex: Sex
  comments(essayId: ID!): [Comment!]
}

enum Sex {
  MALE
  FEMALE
}

type Comment {
  name: String
  mail: String
  content: String
}
```

