# MoMo SMS Data Parser

## Team name

Parsers

## Project description

This project is intended to process MoMo SMS records from XML, clean and categorize them, store them in a relational database, and build a frontend to analyze and visualize the data.

## Members

- James Dovee Kanneh II
- Gavin GANZA
- Herve IMENA Rwigema

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