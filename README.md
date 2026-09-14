# MoMo SMS Data Parser

## Team name

Parsers

## Project description

This project is intended to process MoMo SMS records from XML, clean and categorize them, store them in a relational database, and build a frontend to analyze and visualize the data.

## JSON Data Modeling & Serialization.
### SQL to JSON Serialization Mapping Strategy

To expose our MoMo SQL relational data for external use, we created a structured serialization mapping. The relational database handles complex logic using normalized tables and a junction table (transaction_participants), while the JSON schema utilizes nested structures to reduce API calls and provide full context.

| SQL Database implementation | JSON Serialization Equivalent | Data Type Mapping |
| :--- | :--- | :--- |
| `transactions` Table (Base) | Root `"transaction"` object | `DECIMAL` → `Number (Float)` |
| `transaction_categories` (1:M) | Nested `"category"` object | `INT` FK expands to JSON Object |
| `transaction_participants` (M:N) | `"participants"` JSON Array | Junction table loops into an array of objects containing the specific `role` ENUM |
| `users` (joined via M:N) | Nested `"user"` object within participants | `VARCHAR` → `String`, `ENUM` → `String` |
| `system_logs` (1:M) | `"system_logs"` JSON Array | `DATETIME` → ISO-8601 String (`"YYYY-MM-DDThh:mm:ssZ"`) |

## Members

- James Dovee Kanneh II
- Gavin GANZA
- Herve IMENA Rwigema
- Yai Majak D'Agoot

## Database Design

The database is setup to hold information from the provided Momo transactions data.

### Main Entities

- `users:` stores people or entities involved in transactions
- `transactions:` stores the main transaction records
- `transaction_categories:` classifies transactions in types like payments, transfers, deposits, and airtime purchases
- `transaction_participants:` junction table connecting users and transactions
- `system_logs:` stores processing and ETL logs

The relationship between `users` and `transactions` is many-to-many, which we resolved through `transaction_participants`.

Each transaction belongs to one transaction category, while one category can contain many transactions.

## Related Links

- scrum board: [Github Projects Link](https://github.com/users/imenarh/projects/5/views/1)
- System Architecture: 
    - [Image](/architecture.jpg)
    - [Link](https://miro.com/app/board/uXjVHqIjzts=/)
- Entity Relations Diagram: [Lucid Charts Link](https://lucid.app/lucidchart/2f407223-a5c5-44a1-81aa-a1a2a4dda50f/edit?viewport_loc=-539%2C-343%2C1900%2C1270%2C0_0&invitationId=inv_06b3022b-bc5b-4a05-99eb-6a3b73aaad00)
