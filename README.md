# Conversation Scanner

---
## Description:
>This is a copy of my freelance order. The customer asked not to disclose his data and marketplace.
> 
The program scans conversations from time to time and checks for unread messages. If an unread message appears, he enters the conversation, collects data, and if this message is from a new user, he responds with a pre-prepared message.

---
## Features:
- To store processed conversations and statistics on them, instead of SQL databases, it was decided to use a cheap and simple solution - python module _'shelve'_.
- Due to the fact that the marketplace is written using DOM technology and there are certain difficulties with access to HTML markup, I used a combination of the _'Selenium'_ and '_BeautifulSoup4_' frameworks.
- Apparently the trading platform has a protection system against bots. This is characterized by strange behavior where conversations do not load for a long time. At first, the application crashed and froze at the most unexpected moments. Therefore, it was decided to connect a link to a Telegram notification to the logger

---

## License:

This project is licensed under the MIT License - see the LICENSE file for details
