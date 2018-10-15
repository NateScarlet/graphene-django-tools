Extends [glossary from apollo](https://www.apollographql.com/docs/resources/graphql-glossary.html)

| context           | name      | description                                   |
| ----------------- | --------- | --------------------------------------------- |
| Operation         | info      | Operation resolve information                 |
| Operation         | Node      | A ObjectType that implements field `id`       |
| Mutation          | Create    | Creating data                                 |
| Mutation          | Update    | Modifying data                                |
| Mutation          | Delete    | Deleting data                                 |
| Mutation          | context   | All required data for perform mutation        |
| Mutation          | options   | Operation description provide by server       |
| Mutation          | input     | Wrapped arguments for relay                   |
| Mutation          | arguments | Operation description provide by client       |
| Mutation          | payload   | Client required operation return values       |
| Mutation          | mutate    | Resolve operation and create payload          |
| ModelMutation     | model     | Django db model class for the mutation        |
| ModelMutation     | instance  | Django db model instance for the mutation     |
| ModelMutation     | mapping   | `dict` contains new field values for instance |
| ModelBulkMutation | filters   | Conditions for retrive model from database    |
| ModelBulkMutation | data      | Multiple mapping for multiple instance        |
| ModelBulkMutation | query_set | Django db query set matches filters           |
