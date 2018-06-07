# blog-pure-backend
一个基于 flask 的纯博客后端程序，没有任何前端代码，仅作为一个 GraphQL Server 提供 API。

此后端程序可以跟任意使用 GraphQL 查询语言的 `SPA` 前端博客程序进行组合，

只要其支持下面所谓的 `SGSFB`，全称是 ` Standard GraphQL Schema For Blogs` （笑）

## SGSFB

```graphql
scalar YearTime

input EssayFilter {
    first: Int!
    after: Int
    tag: String
    yearTime: YearTime
}

type Essay {
    essayId: Int
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

type Query {
    essays(essayFilter: EssayFilter!): [Essay!]!
    tags(essayId: Int): [String!]!
    about: About
}
```
